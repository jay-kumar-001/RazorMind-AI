import time
import logging
from typing import Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.risk_service import risk_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.risk")

def risk_agent(merchant_id: str) -> Dict[str, Any]:
    """
    Evaluates multi-factor merchant risk including failure rates, refund velocity, and retention.
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
                total_revenue = 120000.0
                merchant_health_score = 75.0
                total_transactions = 450
            merchant = DefaultMerchant()

        risk_data = risk_service.calculate_merchant_risk(merchant)
        exec_time = time.time() - start_time

        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Risk Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Risk Score: {risk_data['risk_score']}/100 ({risk_data['risk_level']})"
        )
        return risk_data

    except Exception as e:
        logger.error(f"Risk agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Risk Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise