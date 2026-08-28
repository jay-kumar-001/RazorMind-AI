from fastapi import APIRouter, HTTPException
from agents.forecast_agent import forecast_agent
from agents.risk_agent import risk_agent
from agents.decision_agent import decision_agent

router = APIRouter(tags=["Decision"])

@router.get("/decision/{merchant_id}")
def merchant_decision(merchant_id: str):
    """
    Evaluates policy underwriting decision and audit score for a merchant.
    """
    try:
        risk = risk_agent(merchant_id)
        forecast = forecast_agent(merchant_id, months_ahead=3)
        return decision_agent(risk=risk, forecast=forecast, merchant_id=merchant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision evaluation failed: {str(e)}")