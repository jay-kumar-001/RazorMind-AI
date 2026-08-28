import time
import logging
from typing import Dict, Any, Optional
from agents.revenue_agent import get_merchant_data
from backend.database import SessionLocal
from backend.models import Merchant
from backend.routes.traces import save_agent_trace
from backend.services.merchant_context import data_confidence

logger = logging.getLogger("razormind.agent.kpi")


def _portfolio_percentiles(value: float, column: str) -> Optional[float]:
    db = SessionLocal()
    try:
        rows = db.query(getattr(Merchant, column)).all()
        vals = [float(r[0]) for r in rows if r[0] is not None]
        if not vals:
            return None
        below = sum(1 for v in vals if v <= value)
        return round(below / len(vals) * 100.0, 1)
    except Exception:
        return None
    finally:
        db.close()


def kpi_agent(merchant_id: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")
        rev = float(getattr(merchant, "total_revenue", 0.0) or 0.0)
        succ = float(getattr(merchant, "success_rate", 0.0) or 0.0)
        ref = float(getattr(merchant, "refund_rate", 0.0) or 0.0)
        ret = float(getattr(merchant, "retention_score", 0.0) or 0.0)
        health = float(getattr(merchant, "merchant_health_score", 0.0) or 0.0)
        cat = str(getattr(merchant, "category", "E-Commerce") or "E-Commerce")
        tx = int(getattr(merchant, "total_transactions", 0) or 0)
        aov = float(getattr(merchant, "avg_order_value", 0.0) or 0.0)

        success_percentile = _portfolio_percentiles(succ, "success_rate") or round(min(99.0, max(5.0, (succ - 80.0) / 18.0 * 100)), 1)
        raw_refund_pct = _portfolio_percentiles(ref, "refund_rate")
        refund_health_percentile = round(100.0 - raw_refund_pct, 1) if raw_refund_pct is not None else min(99.0, max(5.0, round((5.0 - ref) / 4.5 * 100, 1)))
        retention_percentile = _portfolio_percentiles(ret, "retention_score") or min(99.0, max(5.0, round(ret / 50.0 * 100, 1)))

        benchmarks = {
            "success_rate": {"value": succ, "target": 94.0, "percentile": success_percentile, "status": "Strong" if succ >= 92 else "Needs Improvement"},
            "refund_rate": {"value": ref, "target": 1.5, "percentile": refund_health_percentile, "status": "Optimal" if ref <= 2.0 else "Elevated"},
            "retention_score": {"value": ret, "target": 35.0, "percentile": retention_percentile, "status": "Healthy" if ret >= 25 else "Underperforming"},
            "health_score": {"value": health, "target": 80.0, "status": "Prime" if health >= 75 else "At Risk"},
            "avg_order_value": {"value": aov, "currency": "INR"},
            "total_transactions": {"value": tx},
            "total_revenue": {"value": rev},
        }
        reasoning = (
            f"Portfolio percentile auth {success_percentile}th; refund-health {refund_health_percentile}th; "
            f"retention {retention_percentile}th."
        )
        result = {
            "merchant_id": merchant_id,
            "category": cat,
            "overall_health_score": health,
            "kpi_metrics": benchmarks,
            "operational_grade": "A" if health >= 80 else ("B" if health >= 65 else "C"),
            "reasoning_summary": reasoning,
            "confidence_score": data_confidence(merchant),
        }
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="KPI Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=f"Grade {result['operational_grade']} health {health:.1f}",
            confidence=result["confidence_score"],
            reasoning=reasoning,
        )
        return result
    except Exception as e:
        logger.error("KPI agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="KPI Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
