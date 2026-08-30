import time
import logging
from typing import Dict, Any
from agents.revenue_agent import revenue_agent
from agents.forecast_agent import forecast_agent
from agents.risk_agent import risk_agent
from agents.churn_agent import churn_agent
from agents.kpi_agent import kpi_agent
from agents.rootcause_agent import rootcause_agent
from agents.recommendation_agent import recommendation_agent
from agents.decision_agent import decision_agent
from agents.executive_report_agent import executive_report_agent
from agents.action_plan_agent import action_plan_agent
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.final_report")

def final_report_agent(merchant_id: str) -> Dict[str, Any]:
    """
    Orchestrates and synthesizes a full multi-agent intelligence payload for a merchant.
    """
    start_time = time.time()
    try:
        rev = revenue_agent(merchant_id)
        fc = forecast_agent(merchant_id, months_ahead=3)
        risk = risk_agent(merchant_id)
        churn = churn_agent(merchant_id)
        kpi = kpi_agent(merchant_id)
        rc = rootcause_agent(merchant_id)
        dec = decision_agent(risk, fc, merchant_id=merchant_id, churn=churn)
        exec_rep = executive_report_agent(rev, fc, risk, recs, churn_data=churn, decision_data=dec)
        act_plan = action_plan_agent(merchant_id, risk.get("risk_level", "LOW"), recs)

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Final Report Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Synthesized full intelligence bundle for {merchant_id}"
        )

        return {
            "merchant_id": merchant_id,
            "revenue": rev,
            "forecast": fc,
            "risk": risk,
            "churn": churn,
            "kpi": kpi,
            "root_cause": rc,
            "recommendations": recs,
            "decision": dec,
            "executive_report": exec_rep,
            "action_plan": act_plan,
            "execution_time_seconds": round(exec_time, 3)
        }

    except Exception as e:
        logger.error(f"Final report agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Final Report Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise