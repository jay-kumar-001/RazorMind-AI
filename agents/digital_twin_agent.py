import time
import logging
from typing import Dict, Any, Optional
from agents.revenue_agent import get_merchant_data
from backend.services.simulation_service import simulation_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.digital_twin")

def digital_twin_agent(
    merchant_id: str,
    success_rate_increase: float = 0.0,
    refund_rate_reduction: float = 0.0,
    churn_rate_reduction: float = 0.0,
    retention_increase: float = 0.0,
    volume_growth: float = 0.0,
    simulated_success_rate: Optional[float] = None,
    simulated_refund_rate: Optional[float] = None
) -> Dict[str, Any]:
    """
    Simulates operational parameter shifts and recalculates revenue, risk, health, and forecasts.
    """
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")

        base_succ = float(getattr(merchant, "success_rate", 0.0) or 0.0)
        base_ref = float(getattr(merchant, "refund_rate", 0.0) or 0.0)

        if simulated_success_rate is not None:
            success_delta = simulated_success_rate - base_succ
        else:
            success_delta = success_rate_increase

        if simulated_refund_rate is not None:
            refund_delta = simulated_refund_rate - base_ref
        else:
            refund_delta = -refund_rate_reduction

        churn_delta = -churn_rate_reduction

        result = simulation_service.run_simulation(
            merchant=merchant,
            success_rate_delta=success_delta,
            refund_rate_delta=refund_delta,
            churn_rate_delta=churn_delta,
            retention_delta=retention_increase,
            volume_growth_delta=volume_growth
        )

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Digital Twin Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Simulated Revenue: INR {result['simulated']['revenue']:,.0f} (Shift: {result['simulated']['revenue_growth_percent']:+.1f}%)"
        )
        return result

    except Exception as e:
        logger.error(f"Digital Twin agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Digital Twin Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise