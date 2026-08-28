from fastapi import APIRouter, HTTPException
from graphs.merchant_graph import merchant_graph

router = APIRouter(tags=["LangGraph"])

@router.get("/graph-analysis/{merchant_id}")
def graph_analysis(merchant_id: str):
    """
    Executes the multi-agent graph pipeline and returns structured graph nodes and telemetry.
    """
    try:
        result = merchant_graph.invoke({"merchant_id": merchant_id})
        return {
            "merchant_id": merchant_id,
            "execution_trace": result.get("execution_trace", []),
            "decision_data": result.get("decision_data", {}),
            "recommendations": result.get("recommendations", []),
            "executive_report": result.get("executive_report", ""),
            "action_plan": result.get("action_plan", {}),
            "risk_data": result.get("risk_data", {}),
            "forecast_data": result.get("forecast_data", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph analysis error: {str(e)}")