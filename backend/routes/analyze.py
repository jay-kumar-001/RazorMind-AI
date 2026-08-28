from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import MerchantAnalysis
from graphs.merchant_graph import merchant_graph

router = APIRouter(tags=["Analysis"])

@router.post("/analyze/{merchant_id}")
def trigger_merchant_analysis(merchant_id: str):
    """
    Triggers full multi-agent analysis and persists the result in the database.
    """
    try:
        result = merchant_graph.invoke({"merchant_id": merchant_id})
        return {
            "merchant_id": merchant_id,
            "status": "COMPLETED",
            "decision": result.get("decision_data", {}),
            "risk": result.get("risk_data", {}),
            "revenue": result.get("revenue_data", {}),
            "executive_report": result.get("executive_report", ""),
            "action_plan": result.get("action_plan", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Retrieves historical analysis record by ID.
    """
    analysis = db.query(MerchantAnalysis).filter(MerchantAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": analysis.id,
        "merchant_id": analysis.merchant_id,
        "decision": analysis.decision,
        "risk_level": analysis.risk_level,
        "risk_score": getattr(analysis, "risk_score", 0.0),
        "confidence_score": getattr(analysis, "confidence_score", None),
        "executive_report": analysis.executive_report,
        "action_plan": getattr(analysis, "action_plan", None),
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None
    }
