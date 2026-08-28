from fastapi import APIRouter, HTTPException
from agents.revenue_agent import revenue_agent
from agents.forecast_agent import forecast_agent
from agents.risk_agent import risk_agent
from agents.recommendation_agent import recommendation_agent
from agents.executive_report_agent import executive_report_agent

router = APIRouter(tags=["Executive Report"])

@router.get("/executive-report/{merchant_id}")
def get_executive_report(merchant_id: str):
    """
    Generates an investor-grade executive merchant intelligence report.
    """
    try:
        rev = revenue_agent(merchant_id)
        fc = forecast_agent(merchant_id, months_ahead=3)
        risk = risk_agent(merchant_id)
        recs = recommendation_agent(merchant_id)

        report_text = executive_report_agent(
            revenue_data=rev,
            forecast_data=fc,
            risk_data=risk,
            recommendations=recs
        )

        return {
            "merchant_id": merchant_id,
            "report": report_text,
            "risk_score": risk.get("risk_score"),
            "risk_level": risk.get("risk_level"),
            "confidence_score": risk.get("confidence_score")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive report failed: {str(e)}")
