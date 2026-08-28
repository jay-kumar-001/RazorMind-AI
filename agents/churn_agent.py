import time
import logging
from typing import Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.churn_service import churn_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.churn")


def churn_agent(merchant_id: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")
        churn_data = churn_service.predict_churn(merchant)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Churn Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=f"Churn {churn_data['churn_probability']:.1f}% ({churn_data['churn_risk_level']})",
            confidence=churn_data.get("confidence_score"),
            reasoning=churn_data.get("reasoning_summary"),
            source_metrics=churn_data.get("source_metrics"),
        )
        return churn_data
    except Exception as e:
        logger.error("Churn agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Churn Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
