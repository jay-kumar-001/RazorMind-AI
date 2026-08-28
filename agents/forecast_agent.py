import time
import logging
from typing import List, Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.forecast_service import forecast_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.forecast")


def forecast_agent(merchant_id: str, months_ahead: int = 3) -> List[Dict[str, Any]]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")
        forecast_data = forecast_service.generate_forecast(merchant, months_ahead=months_ahead)
        avg_predicted = sum(f["predicted_revenue"] for f in forecast_data) / max(len(forecast_data), 1)
        conf = forecast_data[0].get("confidence_score") if forecast_data else None
        reasoning = forecast_data[0].get("explanation") if forecast_data else ""
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Forecast Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=f"{months_ahead}-mo avg INR {avg_predicted:,.0f}",
            confidence=conf,
            reasoning=reasoning,
            source_metrics=forecast_data[0].get("source_metrics") if forecast_data else {},
        )
        return forecast_data
    except Exception as e:
        logger.error("Forecast agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Forecast Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
