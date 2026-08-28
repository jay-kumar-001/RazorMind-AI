import time
import logging
from typing import Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.risk_service import risk_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.risk")


def risk_agent(merchant_id: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")
        risk_data = risk_service.calculate_merchant_risk(merchant)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Risk Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=f"Risk {risk_data['risk_score']}/100 ({risk_data['risk_level']})",
            confidence=risk_data.get("confidence_score"),
            reasoning=risk_data.get("reasoning_summary"),
            source_metrics=risk_data.get("source_metrics"),
        )
        return risk_data
    except Exception as e:
        logger.error("Risk agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Risk Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
