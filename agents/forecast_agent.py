import time
import logging
from typing import List, Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.forecast_service import forecast_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.forecast")

def forecast_agent(merchant_id: str, months_ahead: int = 3) -> List[Dict[str, Any]]:
    """
    Generates dynamic multi-month revenue projections with 95% confidence bounds.
    """
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            class DefaultMerchant:
                total_revenue = 120000.0
                merchant_health_score = 75.0
                success_rate = 92.5
                category = "E-Commerce"
                merchant_id = merchant_id
            merchant = DefaultMerchant()

        forecast_data = forecast_service.generate_forecast(merchant, months_ahead=months_ahead)
        exec_time = time.time() - start_time

        avg_predicted = sum(f["predicted_revenue"] for f in forecast_data) / len(forecast_data)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Forecast Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Projected {months_ahead}-month avg: INR {avg_predicted:,.0f}"
        )
        return forecast_data

    except Exception as e:
        logger.error(f"Forecast agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Forecast Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise