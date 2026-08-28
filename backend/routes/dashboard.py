from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Merchant, MerchantAnalysis, AgentExecution

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard")
def dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns executive portfolio intelligence across all active merchants.
    """
    total_merchants = db.query(Merchant).count() or 0
    total_gmv = db.query(func.sum(Merchant.total_revenue)).scalar() or 0.0
    avg_success = db.query(func.avg(Merchant.success_rate)).scalar() or 0.0
    avg_refund = db.query(func.avg(Merchant.refund_rate)).scalar() or 0.0
    avg_health = db.query(func.avg(Merchant.merchant_health_score)).scalar() or 0.0

    # Risk tier segmentation based on risk_score
    low_risk = db.query(Merchant).filter(Merchant.risk_score < 30.0).count()
    medium_risk = db.query(Merchant).filter(
        (Merchant.risk_score >= 30.0) & (Merchant.risk_score < 60.0)
    ).count()
    high_risk = db.query(Merchant).filter(
        (Merchant.risk_score >= 60.0) & (Merchant.risk_score < 80.0)
    ).count()
    critical_risk = db.query(Merchant).filter(Merchant.risk_score >= 80.0).count()

    approved = low_risk
    monitor_closely = medium_risk

    total_analyses = db.query(MerchantAnalysis).count()
    total_agent_runs = db.query(AgentExecution).count()
    avg_h = float(avg_health)

    return {
        "total_merchants": total_merchants,
        "total_gmv": round(float(total_gmv), 2),
        "total_gmv_crore": round(float(total_gmv) / 1e7, 2),
        "avg_success_rate": round(float(avg_success), 2),
        "avg_refund_rate": round(float(avg_refund), 2),
        "avg_health_score": round(avg_h, 1),
        "approved": approved,
        "monitor_closely": monitor_closely,
        "high_risk_merchants": high_risk + critical_risk,
        "high_risk_count": high_risk + critical_risk,  # alias for frontend
        "total_analyses": total_analyses,
        "total_agent_runs": total_agent_runs,
        "portfolio_health_grade": "A" if avg_h >= 80 else ("A-" if avg_h >= 75 else ("B+" if avg_h >= 68 else "B")),
        # Risk distribution for chart
        "risk_distribution": {
            "LOW": low_risk,
            "MEDIUM": medium_risk,
            "HIGH": high_risk,
            "CRITICAL": critical_risk,
        },
    }