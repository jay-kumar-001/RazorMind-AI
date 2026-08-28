import time
import logging
from typing import Dict, Any, List
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.decision")

def decision_agent(
    risk: Dict[str, Any],
    forecast: List[Dict[str, Any]],
    merchant_id: str = "Unknown"
) -> Dict[str, Any]:
    """
    Evaluates multi-criteria underwriting decision based on risk profiles and forward projections.
    """
    start_time = time.time()
    try:
        risk_level = str(risk.get("risk_level", "MEDIUM")).upper()
        risk_score = float(risk.get("risk_score", 50.0))

        if forecast and len(forecast) > 0:
            avg_forecast = sum(item["predicted_revenue"] for item in forecast) / len(forecast)
            growth_trend = forecast[-1]["predicted_revenue"] >= forecast[0]["predicted_revenue"]
        else:
            avg_forecast = 100000.0
            growth_trend = True

        # Multi-tiered policy matrix
        if risk_score <= 25.0 and growth_trend:
            decision = "APPROVE"
            rationale = "Exceptional operational health with stable authorizations and positive forecast trajectory."
            audit_score = 98.0
        elif risk_score <= 45.0:
            decision = "APPROVE WITH MONITORING"
            rationale = "Satisfactory fundamentals with mild authorization or volume variance. Approved for standard limits."
            audit_score = 88.0
        elif risk_score <= 65.0:
            decision = "MONITOR CLOSELY"
            rationale = "Elevated refund rate or declining authorization success. Requires active monitoring and dynamic routing rules."
            audit_score = 74.0
        elif risk_score <= 85.0:
            decision = "HIGH RISK"
            rationale = "Substantial operational risk identified. Recommend lower transaction velocity limits and dispute safeguards."
            audit_score = 55.0
        else:
            decision = "REQUIRES IMMEDIATE INTERVENTION"
            rationale = "Critical failure thresholds breached. Automatic hold on limit expansion; merchant audit mandated."
            audit_score = 30.0

        confidence = round(min(99.0, max(85.0, 95.0 - (risk_score * 0.1))), 1)

        result = {
            "final_decision": decision,
            "decision_rationale": rationale,
            "risk_tier": risk_level,
            "risk_score": risk_score,
            "projected_3mo_avg": round(avg_forecast, 2),
            "audit_score": audit_score,
            "confidence_score": confidence
        }

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Decision Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Decision: {decision} (Audit Score: {audit_score})"
        )
        return result

    except Exception as e:
        logger.error(f"Decision agent error: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Decision Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise