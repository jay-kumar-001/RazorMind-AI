from fastapi import APIRouter, HTTPException
from graphs.merchant_graph import merchant_graph

router = APIRouter(tags=["LangGraph"])

@router.get("/agent-report/{merchant_id}")
def agent_report(merchant_id: str):
    """
    Executes the multi-agent LangGraph workflow pipeline and returns the synthesized report.
    """
    try:
        result = merchant_graph.invoke({"merchant_id": merchant_id})
        return {
            "merchant_id": merchant_id,
            "decision": result.get("decision_data", {}),
            "risk": result.get("risk_data", {}),
            "revenue": result.get("revenue_data", {}),
            "forecast": result.get("forecast_data", []),
            "root_cause": result.get("rootcause_data", {}),
            "kpi": result.get("kpi_data", {}),
            "recommendations": result.get("recommendations", []),
            "action_plan": result.get("action_plan", {}),
            "executive_report": result.get("executive_report", ""),
            "execution_trace": result.get("execution_trace", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")