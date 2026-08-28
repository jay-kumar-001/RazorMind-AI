from fastapi import APIRouter, HTTPException
from agents.action_plan_agent import action_plan_agent
from agents.risk_agent import risk_agent

router = APIRouter(tags=["Action Plan"])

@router.get("/action-plan/{merchant_id}")
def get_action_plan(merchant_id: str):
    """
    Generates a personalized, tactical 30-day action plan for a merchant.
    """
    try:
        risk_data = risk_agent(merchant_id)
        return action_plan_agent(
            merchant_id=merchant_id,
            risk_level=risk_data.get("risk_level", "LOW"),
            recommendations=risk_data.get("recommendations", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action plan generation failed: {str(e)}")