import time
import logging
from typing import Dict, Any
from backend.services.merchant_context import get_merchant_snapshot, snapshot_metrics, data_confidence
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.revenue")


def get_merchant_data(merchant_id: str):
    return get_merchant_snapshot(merchant_id)


def revenue_agent(merchant_id: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")

        total_rev = float(getattr(merchant, "total_revenue", 0.0) or 0.0)
        success_rate = float(getattr(merchant, "success_rate", 0.0) or 0.0)
        refund_rate = float(getattr(merchant, "refund_rate", 0.0) or 0.0)
        tot_tx = int(getattr(merchant, "total_transactions", 0) or 0)
        aov = float(getattr(merchant, "avg_order_value", 0.0) or (total_rev / max(tot_tx, 1)))
        cat = str(getattr(merchant, "category", "E-Commerce") or "E-Commerce")
        status = str(getattr(merchant, "merchant_status", "ACTIVE") or "ACTIVE")

        net_revenue = round(total_rev * (1.0 - refund_rate / 100.0), 2)
        refunded_amount = round(total_rev * (refund_rate / 100.0), 2)
        revenue_velocity_daily = round(total_rev / 30.0, 2)
        confidence_score = data_confidence(merchant)
        reasoning = (
            f"Run-rate INR {total_rev:,.0f} from {tot_tx} txns, AOV {aov:,.0f}. "
            f"Net after {refund_rate:.2f}% refunds = INR {net_revenue:,.0f}."
        )

        result = {
            "merchant_id": merchant_id,
            "total_revenue": total_rev,
            "net_revenue": net_revenue,
            "refunded_amount": refunded_amount,
            "success_rate": success_rate,
            "refund_rate": refund_rate,
            "chargeback_rate": float(getattr(merchant, "chargeback_rate", 0.0) or 0.0),
            "total_transactions": tot_tx,
            "avg_order_value": aov,
            "revenue_velocity_daily": revenue_velocity_daily,
            "category": cat,
            "status": status,
            "confidence_score": confidence_score,
            "growth_trend": "Positive" if success_rate >= 90.0 else "Declining",
            "reasoning_summary": reasoning,
            "source_metrics": snapshot_metrics(merchant),
            "data_source": getattr(merchant, "data_source", "unknown"),
        }

        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Revenue Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=f"GMV INR {total_rev:,.0f}; auth {success_rate:.1f}%",
            confidence=confidence_score,
            reasoning=reasoning,
            source_metrics=result["source_metrics"],
        )
        return result
    except Exception as e:
        logger.error("Revenue agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Revenue Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
