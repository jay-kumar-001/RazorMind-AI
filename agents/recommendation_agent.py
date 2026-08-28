import time
import logging
from typing import List, Dict, Any
from agents.revenue_agent import get_merchant_data
from backend.services.risk_service import risk_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.recommendation")

def recommendation_agent(merchant_id: str) -> List[str]:
    """
    Generates tailored, high-impact tactical recommendations for a merchant.
    """
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            recommendations = [
                "Enable Smart Retry System for recurring authorizations",
                "Deploy Dynamic Payment Gateway Routing",
                "Implement instant checkout tokenization"
            ]
        else:
            risk_data = risk_service.calculate_merchant_risk(merchant)
            recommendations = risk_data.get("recommendations", [])

            # Ensure rich recommendations list
            total_rev = float(getattr(merchant, "total_revenue", 100000.0) or 100000.0)
            if total_rev < 80000.0:
                recommendations.append("Launch promotional customer acquisition incentive")

        # De-duplicate while preserving order
        unique_recs = list(dict.fromkeys(recommendations))
        if not unique_recs:
            unique_recs = [
                "Maintain active gateway redundancy",
                "Review tier eligibility for volume fee discounts"
            ]

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Recommendation Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Generated {len(unique_recs)} tailored recommendations"
        )
        return unique_recs

    except Exception as e:
        logger.error(f"Recommendation agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Recommendation Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise