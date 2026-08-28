from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from backend.database import get_db
from backend.models import MerchantAnalysis
from agents.revenue_agent import get_merchant_data
from agents.risk_agent import risk_agent
from agents.forecast_agent import forecast_agent
from agents.churn_agent import churn_agent
from agents.rootcause_agent import rootcause_agent
from agents.recommendation_agent import recommendation_agent
from agents.decision_agent import decision_agent
from agents.action_plan_agent import action_plan_agent
from agents.executive_report_agent import executive_report_agent

router = APIRouter(tags=["Intelligence"])


@router.get("/merchant/{merchant_id}/explain-risk")
def explain_risk(merchant_id: str):
    merchant = get_merchant_data(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_id} not found")
    risk = risk_agent(merchant_id)
    root = rootcause_agent(merchant_id)
    churn = churn_agent(merchant_id)
    return {
        "merchant_id": merchant_id,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "confidence_score": risk.get("confidence_score"),
        "model": risk.get("model"),
        "feature_importance": risk.get("feature_importance"),
        "factor_breakdown": risk.get("factor_breakdown"),
        "top_driver": risk.get("top_driver"),
        "explanation": risk.get("explanation"),
        "risk_factors": risk.get("risk_factors"),
        "root_cause": root,
        "churn": {
            "probability": churn.get("churn_probability"),
            "explanation": churn.get("explanation"),
            "feature_importance": churn.get("feature_importance"),
            "model": churn.get("model"),
        },
    }


@router.get("/compare-merchants")
def compare_merchants(ids: str = Query(..., description="Comma-separated merchant IDs")):
    merchant_ids = [x.strip().upper() for x in ids.split(",") if x.strip()][:8]
    if len(merchant_ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two merchant IDs")
    rows = []
    for mid in merchant_ids:
        m = get_merchant_data(mid)
        if not m:
            rows.append({"merchant_id": mid, "error": "not_found"})
            continue
        risk = risk_agent(mid)
        churn = churn_agent(mid)
        fc = forecast_agent(mid, months_ahead=3)
        rows.append({
            "merchant_id": mid,
            "merchant_name": getattr(m, "merchant_name", mid),
            "category": getattr(m, "category", None),
            "total_revenue": float(getattr(m, "total_revenue", 0) or 0),
            "success_rate": float(getattr(m, "success_rate", 0) or 0),
            "refund_rate": float(getattr(m, "refund_rate", 0) or 0),
            "health": float(getattr(m, "merchant_health_score", 0) or 0),
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "churn_probability": churn["churn_probability"],
            "month_plus_1": fc[0]["predicted_revenue"] if fc else None,
            "decision": decision_agent(risk, fc, merchant_id=mid, churn=churn)["final_decision"],
        })
    return {"merchants": rows}


@router.get("/merchant/{merchant_id}/what-changed")
def what_changed(merchant_id: str, db: Session = Depends(get_db)):
    analyses = (
        db.query(MerchantAnalysis)
        .filter(MerchantAnalysis.merchant_id == merchant_id)
        .order_by(MerchantAnalysis.id.desc())
        .limit(5)
        .all()
    )
    current = {
        "risk": risk_agent(merchant_id),
        "churn": churn_agent(merchant_id),
    }
    if len(analyses) < 2:
        return {
            "merchant_id": merchant_id,
            "message": "Not enough historical runs to diff. Showing live vs last stored analysis.",
            "live_risk_score": current["risk"]["risk_score"],
            "last_stored": {
                "risk_score": analyses[0].risk_score if analyses else None,
                "decision": analyses[0].decision if analyses else None,
                "created_at": analyses[0].created_at.isoformat() if analyses and analyses[0].created_at else None,
            },
            "delta_risk": round(current["risk"]["risk_score"] - (analyses[0].risk_score or 0), 2) if analyses else None,
        }
    newest, prev = analyses[0], analyses[1]
    return {
        "merchant_id": merchant_id,
        "latest_run": newest.created_at.isoformat() if newest.created_at else None,
        "previous_run": prev.created_at.isoformat() if prev.created_at else None,
        "decision_from": prev.decision,
        "decision_to": newest.decision,
        "risk_from": prev.risk_score,
        "risk_to": newest.risk_score,
        "delta_risk": round((newest.risk_score or 0) - (prev.risk_score or 0), 2),
        "live_risk_score": current["risk"]["risk_score"],
        "live_churn": current["churn"]["churn_probability"],
    }


@router.get("/due-diligence/{merchant_id}")
def due_diligence(merchant_id: str):
    merchant = get_merchant_data(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_id} not found")
    risk = risk_agent(merchant_id)
    fc = forecast_agent(merchant_id, months_ahead=3)
    churn = churn_agent(merchant_id)
    root = rootcause_agent(merchant_id)
    recs = recommendation_agent(merchant_id)
    dec = decision_agent(risk, fc, merchant_id=merchant_id, churn=churn)
    plan = action_plan_agent(merchant_id, risk.get("risk_level"), recs, use_llm=False)
    brief = executive_report_agent(
        revenue_data={
            "merchant_id": merchant_id,
            "total_revenue": getattr(merchant, "total_revenue", 0),
            "success_rate": getattr(merchant, "success_rate", 0),
            "refund_rate": getattr(merchant, "refund_rate", 0),
            "avg_order_value": getattr(merchant, "avg_order_value", 0),
        },
        forecast_data=fc,
        risk_data=risk,
        recommendations=recs,
        use_llm=False,
    )
    return {
        "merchant_id": merchant_id,
        "merchant_name": getattr(merchant, "merchant_name", merchant_id),
        "decision": dec,
        "risk": risk,
        "forecast": fc,
        "churn": churn,
        "root_cause": root,
        "recommendations": recs,
        "action_plan": plan,
        "boardroom_briefing": brief,
        "confidence_score": dec.get("confidence_score"),
    }
