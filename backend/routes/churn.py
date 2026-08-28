from fastapi import APIRouter, HTTPException
from agents.churn_agent import churn_agent

router = APIRouter(tags=["Churn"])

@router.get("/merchant/{merchant_id}/churn")
def get_churn(merchant_id: str):
    """
    Returns ML churn prediction, key retention drivers, and proactive mitigation playbook.
    """
    try:
        return churn_agent(merchant_id=merchant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Churn calculation failed: {str(e)}")