import time
import logging
from typing import Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.churn_service import churn_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.churn")

def churn_agent(merchant_id: str) -> Dict[str, Any]:
    """
    Analyzes merchant churn propensity and key behavioral drag factors.
    """
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            class DefaultMerchant:
                merchant_id = merchant_id
                success_rate = 92.5
                refund_rate = 1.8
                retention_score = 30.0
                merchant_health_score = 75.0
                risk_score = 25.0
                total_revenue = 120000.0
            merchant = DefaultMerchant()

        churn_data = churn_service.predict_churn(merchant)
        exec_time = time.time() - start_time

        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Churn Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Churn Prob: {churn_data['churn_probability']:.1f}% ({churn_data['churn_risk_level']})"
        )
        return churn_data

    except Exception as e:
        logger.error(f"Churn agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Churn Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise