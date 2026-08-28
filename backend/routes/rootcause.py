from fastapi import APIRouter, HTTPException
from agents.rootcause_agent import rootcause_agent
from agents.kpi_agent import kpi_agent

router = APIRouter(tags=["Root Cause"])

@router.get("/merchant/{merchant_id}/root-cause")
def get_root_cause_analysis(merchant_id: str):
    """
    Returns deep diagnostic signals, primary bottlenecks, and failure attribution for a merchant.
    """
    try:
        rc = rootcause_agent(merchant_id)
        kpi = kpi_agent(merchant_id)
        return {
            "merchant_id": merchant_id,
            "primary_bottleneck": rc.get("primary_bottleneck"),
            "diagnosed_issues": rc.get("diagnosed_issues", []),
            "kpi_benchmarks": kpi.get("kpi_metrics", {}),
            "operational_grade": kpi.get("operational_grade", "B"),
            "confidence_score": rc.get("confidence_score", 93.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Root cause analysis failed: {str(e)}")
