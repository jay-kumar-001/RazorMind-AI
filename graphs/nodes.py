import time
import logging
import json
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

from backend.database import SessionLocal
from backend.models import AgentExecution, MerchantAnalysis

logger = logging.getLogger("razormind.graph.nodes")

def add_trace(state: Dict[str, Any], agent_name: str, status: str = "completed", duration_ms: float = 0.0):
    if "execution_trace" not in state:
        state["execution_trace"] = []
    state["execution_trace"].append({
        "agent": agent_name,
        "status": status,
        "duration_ms": round(duration_ms, 2)
    })

def save_analysis(state: Dict[str, Any]):
    """
    Saves complete analysis run to database for history, auditing, and trend tracking.
    """
    db = SessionLocal()
    try:
        m_id = state.get("merchant_id", "Unknown")
        decision_val = state.get("decision_data", {}).get("final_decision", "APPROVE")
        risk_lvl = state.get("risk_data", {}).get("risk_level", "LOW")
        risk_score = state.get("risk_data", {}).get("risk_score")
        report_text = state.get("executive_report", "")
        plan_text = state.get("action_plan", {}).get("action_plan", "")
        root_causes = json.dumps(state.get("rootcause_data", {}))
        recs = json.dumps(state.get("recommendations", []))

        analysis = MerchantAnalysis(
            merchant_id=m_id,
            decision=decision_val,
            risk_level=risk_lvl,
            risk_score=risk_score,
            confidence_score=state.get("decision_data", {}).get("confidence_score"),
            executive_report=report_text,
            action_plan=plan_text,
            root_causes=root_causes,
            recommendations=recs
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        state["analysis_id"] = analysis.id
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving merchant analysis to DB: {e}")
    finally:
        db.close()


def revenue_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["revenue_data"] = revenue_agent(state["merchant_id"])
    add_trace(state, "Revenue Agent", duration_ms=(time.time() - start) * 1000)
    return state

def forecast_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["forecast_data"] = forecast_agent(state["merchant_id"], months_ahead=3)
    add_trace(state, "Forecast Agent", duration_ms=(time.time() - start) * 1000)
    return state

def risk_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["risk_data"] = risk_agent(state["merchant_id"])
    add_trace(state, "Risk Agent", duration_ms=(time.time() - start) * 1000)
    return state

def churn_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["churn_data"] = churn_agent(state["merchant_id"])
    add_trace(state, "Churn Agent", duration_ms=(time.time() - start) * 1000)
    return state

def kpi_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["kpi_data"] = kpi_agent(state["merchant_id"])
    add_trace(state, "KPI Agent", duration_ms=(time.time() - start) * 1000)
    return state

def rootcause_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["rootcause_data"] = rootcause_agent(state["merchant_id"])
    add_trace(state, "Root Cause Agent", duration_ms=(time.time() - start) * 1000)
    return state

def recommendation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["recommendations"] = recommendation_agent(state["merchant_id"])
    add_trace(state, "Recommendation Agent", duration_ms=(time.time() - start) * 1000)
    return state

def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["decision_data"] = decision_agent(
        risk=state.get("risk_data", {}),
        forecast=state.get("forecast_data", []),
        merchant_id=state.get("merchant_id", "Unknown"),
        churn=state.get("churn_data", {}),
    )
    add_trace(state, "Decision Agent", duration_ms=(time.time() - start) * 1000)
    return state

def action_plan_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["action_plan"] = action_plan_agent(
        merchant_id=state["merchant_id"],
        risk_level=state.get("risk_data", {}).get("risk_level", "LOW"),
        recommendations=state.get("recommendations", []),
        use_llm=False,
    )
    add_trace(state, "Action Plan Agent", duration_ms=(time.time() - start) * 1000)
    return state

def executive_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    state["executive_report"] = executive_report_agent(
        revenue_data=state.get("revenue_data", {}),
        forecast_data=state.get("forecast_data", []),
        risk_data=state.get("risk_data", {}),
        recommendations=state.get("recommendations", []),
        use_llm=False,
    )
    state["final_report"] = {
        "merchant_id": state.get("merchant_id"),
        "decision": state.get("decision_data"),
        "risk": state.get("risk_data"),
        "revenue": state.get("revenue_data"),
        "forecast": state.get("forecast_data"),
        "executive_report": state.get("executive_report"),
        "action_plan": state.get("action_plan")
    }
    save_analysis(state)
    add_trace(state, "Executive Report Agent", duration_ms=(time.time() - start) * 1000)
    return state
