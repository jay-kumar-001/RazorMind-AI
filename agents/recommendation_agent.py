import time
import logging
from typing import List, Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.risk_service import risk_service
from backend.services.churn_service import churn_service
from backend.services.forecast_service import forecast_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.recommendation")


def recommendation_agent(merchant_id: str) -> List[str]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")
        risk_data = risk_service.calculate_merchant_risk(merchant)
        churn_data = churn_service.predict_churn(merchant)
        fc = forecast_service.generate_forecast(merchant, months_ahead=3)
        recs = list(risk_data.get("recommendations") or [])
        if churn_data.get("churn_probability", 0) >= 50:
            recs.append(churn_data.get("recommended_playbook"))
        if fc:
            slope = fc[-1].get("growth_percent", 0)
            if slope < 0:
                recs.append(
                    f"Revenue trajectory {slope}% over horizon — pair auth recovery with volume campaigns"
                )
        unique = [r for r in dict.fromkeys(recs) if r]
        reasoning = f"{len(unique)} recs from risk={risk_data['risk_level']} churn={churn_data['churn_probability']}%"
        rec_conf = round(float((risk_data.get("confidence_score") or 75.0) * 0.6 + (churn_data.get("confidence_score") or 75.0) * 0.4), 1)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Recommendation Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=reasoning,
            confidence=rec_conf,
            reasoning=reasoning,
            source_metrics=risk_data.get("source_metrics"),
        )
        return unique
    except Exception as e:
        logger.error("Recommendation agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Recommendation Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
