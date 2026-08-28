from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Merchant
from backend.services.merchant_context import get_merchant_snapshot

router = APIRouter(tags=["Merchants"])

@router.get("/merchants")
def list_merchants(
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns merchant directory with search and filtering for dropdowns and portfolio analysis.
    """
    query = db.query(Merchant)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Merchant.merchant_id.ilike(search_pattern)) |
            (Merchant.merchant_name.ilike(search_pattern))
        )
    if category:
        query = query.filter(Merchant.category == category)
    if status:
        query = query.filter(Merchant.merchant_status == status)

    total = query.count()
    # Support page-based or offset-based pagination
    eff_offset = (page - 1) * limit if offset == 0 else offset
    merchants_raw = query.order_by(Merchant.id.asc()).offset(eff_offset).limit(limit).all()

    items = [
        {
            "merchant_id": m.merchant_id,
            "merchant_name": m.merchant_name,
            "category": m.category,
            "industry": m.industry,
            "total_revenue": m.total_revenue,
            "success_rate": m.success_rate,
            "refund_rate": m.refund_rate,
            "merchant_health_score": m.merchant_health_score,
            "merchant_status": m.merchant_status,
            "risk_score": m.risk_score
        }
        for m in merchants_raw
    ]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "offset": eff_offset,
        "merchants": items,  # frontend key
        "items": items,       # legacy key
    }



@router.get("/merchant/{merchant_id}")
def get_merchant(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves full merchant profile from PostgreSQL.
    """
    merchant = db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_id} not found.")

    snap = get_merchant_snapshot(merchant_id)

    return {
        "merchant_id": merchant.merchant_id,
        "merchant_name": merchant.merchant_name or f"Merchant {merchant.merchant_id}",
        "category": merchant.category or "E-Commerce",
        "industry": merchant.industry or "Retail",
        "total_revenue": merchant.total_revenue or 0.0,
        "total_transactions": merchant.total_transactions or 0,
        "success_rate": merchant.success_rate or 0.0,
        "refund_rate": merchant.refund_rate or 0.0,
        "active_customers": merchant.active_customers or 0,
        "repeat_customers": merchant.repeat_customers or 0,
        "avg_order_value": merchant.avg_order_value or 0.0,
        "revenue_score": merchant.revenue_score or 0.0,
        "retention_score": merchant.retention_score or 0.0,
        "risk_score": merchant.risk_score or round(100.0 - (merchant.merchant_health_score or 0.0), 2),
        "merchant_health_score": merchant.merchant_health_score or 0.0,
        "merchant_status": merchant.merchant_status or "Healthy",
        "chargeback_rate": float(getattr(snap, "chargeback_rate", 0) or 0) if snap else 0.0,
        "retention_rate": float(getattr(snap, "retention_rate", 0) or (merchant.retention_score or 0)),
        "data_source": getattr(snap, "data_source", "postgres") if snap else "postgres",
        "created_at": merchant.created_at.isoformat() if merchant.created_at else None
    }