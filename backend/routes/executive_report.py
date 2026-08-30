from fastapi import APIRouter, HTTPException
from agents.revenue_agent import revenue_agent
from agents.forecast_agent import forecast_agent
from agents.risk_agent import risk_agent
from agents.churn_agent import churn_agent
from agents.decision_agent import decision_agent
from agents.recommendation_agent import recommendation_agent
from agents.executive_report_agent import executive_report_agent

router = APIRouter(tags=["Executive Report"])

@router.get("/executive-report/{merchant_id}")
def get_executive_report(merchant_id: str):
    """
    Generates an investor-grade executive merchant intelligence report grounded in all upstream specialist signals.
    """
    try:
        rev = revenue_agent(merchant_id)
        fc = forecast_agent(merchant_id, months_ahead=3)
        risk = risk_agent(merchant_id)
        churn = churn_agent(merchant_id)
        recs = recommendation_agent(merchant_id)
        dec = decision_agent(risk=risk, forecast=fc, merchant_id=merchant_id, churn=churn)

        # Derived committee confidence
        risk_conf = float((risk or {}).get("confidence_score") or 75.0)
        fc_conf = float(((fc[0] if fc else {})).get("confidence_score") or 75.0)
        churn_conf = float((churn or {}).get("confidence_score") or 75.0)
        derived_conf = round((risk_conf * 0.40 + fc_conf * 0.35 + churn_conf * 0.25), 1)

        report_text = executive_report_agent(
            revenue_data=rev,
            forecast_data=fc,
            risk_data=risk,
            recommendations=recs,
            churn_data=churn,
            decision_data=dec,
        )

        return {
            "merchant_id": merchant_id,
            "report": report_text,
            "risk_score": risk.get("risk_score"),
            "risk_level": risk.get("risk_level"),
            "churn_probability": churn.get("churn_probability"),
            "decision": dec.get("final_decision"),
            "confidence_score": derived_conf
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive report failed: {str(e)}")
