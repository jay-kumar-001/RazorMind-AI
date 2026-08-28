import logging
import os
from types import SimpleNamespace
from typing import Any, Optional

import pandas as pd

from backend.database import SessionLocal
from backend.models import Merchant
from backend.services.ttl_cache import merchant_cache

logger = logging.getLogger("razormind.merchant_context")

CSV_PATH = "datasets/merchant_kpis.csv"
_csv_df = None


def _kpi_frame() -> Optional[pd.DataFrame]:
    global _csv_df
    if _csv_df is not None:
        return _csv_df
    if not os.path.exists(CSV_PATH):
        return None
    try:
        _csv_df = pd.read_csv(CSV_PATH)
        return _csv_df
    except Exception as e:
        logger.warning("Could not load merchant KPI CSV: %s", e)
        return None


def _row_to_namespace(row: Any) -> SimpleNamespace:
    data = row.to_dict() if hasattr(row, "to_dict") else dict(row)
    retention = data.get("retention_score")
    if retention is None or (isinstance(retention, float) and pd.isna(retention)):
        retention = data.get("retention_rate", 0.0)
    ns = SimpleNamespace()
    ns.merchant_id = str(data.get("merchant_id", ""))
    ns.merchant_name = str(data.get("merchant_name") or ns.merchant_id)
    ns.category = str(data.get("category") or "E-Commerce")
    ns.industry = str(data.get("industry") or ns.category)
    ns.total_revenue = float(data.get("total_revenue") or 0.0)
    ns.total_transactions = int(data.get("total_transactions") or 0)
    ns.success_rate = float(data.get("success_rate") or 0.0)
    ns.refund_rate = float(data.get("refund_rate") or 0.0)
    ns.chargeback_rate = float(data.get("chargeback_rate") or 0.0)
    ns.active_customers = int(data.get("active_customers") or 0)
    ns.repeat_customers = int(data.get("repeat_customers") or 0)
    ns.avg_order_value = float(data.get("avg_order_value") or 0.0)
    ns.revenue_score = float(data.get("revenue_score") or 0.0)
    ns.retention_score = float(retention or 0.0)
    ns.retention_rate = float(data.get("retention_rate") or ns.retention_score)
    ns.risk_score = float(data.get("risk_score") or 0.0)
    ns.merchant_health_score = float(data.get("merchant_health_score") or 0.0)
    ns.merchant_status = str(data.get("merchant_status") or "ACTIVE")
    ns.data_source = "csv"
    return ns


def _orm_to_namespace(m: Merchant, csv_row: Optional[Any] = None) -> SimpleNamespace:
    ns = SimpleNamespace()
    ns.merchant_id = m.merchant_id
    ns.merchant_name = m.merchant_name or m.merchant_id
    ns.category = m.category or "E-Commerce"
    ns.industry = m.industry or ns.category
    ns.total_revenue = float(m.total_revenue or 0.0)
    ns.total_transactions = int(m.total_transactions or 0)
    ns.success_rate = float(m.success_rate or 0.0)
    ns.refund_rate = float(m.refund_rate or 0.0)
    ns.active_customers = int(m.active_customers or 0)
    ns.repeat_customers = int(m.repeat_customers or 0)
    ns.avg_order_value = float(m.avg_order_value or 0.0)
    ns.revenue_score = float(m.revenue_score or 0.0)
    ns.retention_score = float(m.retention_score or 0.0)
    ns.risk_score = float(m.risk_score or 0.0)
    ns.merchant_health_score = float(m.merchant_health_score or 0.0)
    ns.merchant_status = m.merchant_status or "ACTIVE"
    ns.chargeback_rate = 0.0
    ns.retention_rate = ns.retention_score
    ns.data_source = "postgres"

    if csv_row is not None:
        extra = _row_to_namespace(csv_row)
        ns.chargeback_rate = extra.chargeback_rate
        ns.retention_rate = extra.retention_rate
        if ns.retention_score in (0.0, 25.0) and extra.retention_rate:
            ns.retention_score = extra.retention_rate
        if not ns.repeat_customers and extra.repeat_customers:
            ns.repeat_customers = extra.repeat_customers
        ns.data_source = "postgres+csv"
    return ns


def get_merchant_snapshot(merchant_id: str) -> Optional[SimpleNamespace]:
    cached = merchant_cache.get(merchant_id)
    if cached is not None:
        return cached

    csv_row = None
    df = _kpi_frame()
    if df is not None and "merchant_id" in df.columns:
        match = df[df["merchant_id"].astype(str) == str(merchant_id)]
        if not match.empty:
            csv_row = match.iloc[0]

    db = SessionLocal()
    try:
        m = db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()
        if m:
            snap = _orm_to_namespace(m, csv_row)
            merchant_cache.set(merchant_id, snap)
            return snap
    except Exception as e:
        logger.warning("DB merchant read failed for %s: %s", merchant_id, e)
    finally:
        db.close()

    if csv_row is not None:
        snap = _row_to_namespace(csv_row)
        merchant_cache.set(merchant_id, snap)
        return snap
    return None


def snapshot_metrics(merchant: Any) -> dict:
    return {
        "merchant_id": getattr(merchant, "merchant_id", None),
        "total_revenue": float(getattr(merchant, "total_revenue", 0) or 0),
        "success_rate": float(getattr(merchant, "success_rate", 0) or 0),
        "refund_rate": float(getattr(merchant, "refund_rate", 0) or 0),
        "chargeback_rate": float(getattr(merchant, "chargeback_rate", 0) or 0),
        "retention_score": float(getattr(merchant, "retention_score", 0) or 0),
        "merchant_health_score": float(getattr(merchant, "merchant_health_score", 0) or 0),
        "total_transactions": int(getattr(merchant, "total_transactions", 0) or 0),
        "avg_order_value": float(getattr(merchant, "avg_order_value", 0) or 0),
        "category": str(getattr(merchant, "category", "") or ""),
        "data_source": str(getattr(merchant, "data_source", "unknown") or "unknown"),
    }


def data_confidence(merchant: Any) -> float:
    """Confidence from completeness and sample size — not a fake 95%."""
    tx = int(getattr(merchant, "total_transactions", 0) or 0)
    fields = [
        getattr(merchant, "total_revenue", 0),
        getattr(merchant, "success_rate", 0),
        getattr(merchant, "refund_rate", None),
        getattr(merchant, "retention_score", 0),
        getattr(merchant, "merchant_health_score", 0),
    ]
    filled = sum(1 for f in fields if f is not None)
    completeness = filled / max(len(fields), 1)
    volume = min(1.0, tx / 800.0) if tx else 0.25
    score = 55.0 + completeness * 25.0 + volume * 15.0
    return round(min(97.0, max(40.0, score)), 1)
