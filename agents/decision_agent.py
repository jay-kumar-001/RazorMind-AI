import time
import logging
from typing import Dict, Any, List
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.decision")


def decision_agent(
    risk: Dict[str, Any],
    forecast: List[Dict[str, Any]],
    merchant_id: str = "Unknown",
    churn: Dict[str, Any] = None,
) -> Dict[str, Any]:
    start_time = time.time()
    try:
        risk_level = str(risk.get("risk_level", "MEDIUM")).upper()
        risk_score = float(risk.get("risk_score", 50.0))
        churn_p = float((churn or {}).get("churn_probability") or 0.0)

        if forecast:
            avg_forecast = sum(item["predicted_revenue"] for item in forecast) / len(forecast)
            growth_trend = forecast[-1]["predicted_revenue"] >= forecast[0]["predicted_revenue"]
        else:
            avg_forecast = 0.0
            growth_trend = True

        if risk_score <= 25.0 and growth_trend and churn_p < 40:
            decision = "APPROVE"
            rationale = (
                f"Risk {risk_score:.1f} (LOW band), forward GMV rising, churn {churn_p:.1f}%. "
                f"Factors: {', '.join(risk.get('risk_factors', [])[:2])}"
            )
        elif risk_score <= 45.0 and churn_p < 55:
            decision = "APPROVE WITH MONITORING"
            rationale = (
                f"Risk {risk_score:.1f} with mild variance. Auth/refund watch. Churn {churn_p:.1f}%."
            )
        elif risk_score <= 65.0:
            decision = "MONITOR CLOSELY"
            rationale = (
                f"Elevated score {risk_score:.1f} ({risk_level}). "
                f"Primary driver {risk.get('top_driver', 'n/a')}. Churn {churn_p:.1f}%."
            )
        elif risk_score <= 85.0:
            decision = "HIGH RISK"
            rationale = (
                f"Operational risk {risk_score:.1f}. Recommend velocity caps and dispute controls."
            )
        else:
            decision = "REQUIRES IMMEDIATE INTERVENTION"
            rationale = (
                f"Critical score {risk_score:.1f}. Hold limit expansion pending audit."
            )

        # Derive decision confidence directly from upstream model signals (risk, forecast, churn)
        risk_conf = float(risk.get("confidence_score") or 75.0)
        fc_conf = float((forecast[0] if forecast else {}).get("confidence_score") or 75.0)
        churn_conf = float((churn or {}).get("confidence_score") or 75.0)
        confidence = round((risk_conf * 0.45 + fc_conf * 0.30 + churn_conf * 0.25), 1)
        if not forecast:
            confidence = round(confidence - 6.0, 1)
        confidence = round(min(97.0, max(45.0, confidence)), 1)

        result = {
            "final_decision": decision,
            "decision_rationale": rationale,
            "risk_tier": risk_level,
            "risk_score": risk_score,
            "projected_3mo_avg": round(avg_forecast, 2),
            "audit_score": round(max(10.0, 100.0 - risk_score), 1),
            "confidence_score": confidence,
            "reasoning_summary": rationale,
            "source_metrics": {
                "risk_score": risk_score,
                "churn_probability": churn_p,
                "forecast_points": len(forecast or []),
            },
        }
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Decision Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=f"{decision} (conf {confidence}%)",
            confidence=confidence,
            reasoning=rationale,
            source_metrics=result["source_metrics"],
        )
        return result
    except Exception as e:
        logger.error("Decision agent error: %s", e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Decision Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
