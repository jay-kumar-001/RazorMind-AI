from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from agents.digital_twin_agent import digital_twin_agent

router = APIRouter(tags=["Digital Twin"])

class SimulationRequest(BaseModel):
    merchant_id: str
    success_rate_increase: float = Field(0.0, description="Authorization success rate lift percentage, e.g. +5%")
    refund_rate_reduction: float = Field(0.0, description="Refund rate reduction percentage, e.g. 2%")
    churn_rate_reduction: float = Field(0.0, description="Churn probability reduction percentage, e.g. 5%")
    retention_increase: float = Field(0.0, description="Repeat customer retention boost percentage, e.g. 10%")
    volume_growth: float = Field(0.0, description="Exogenous transaction volume expansion percentage, e.g. 15%")

@router.post("/simulate")
def simulate_merchant(payload: SimulationRequest):
    """
    Executes what-if parameter simulation on merchant Digital Twin.
    """
    try:
        return digital_twin_agent(
            merchant_id=payload.merchant_id,
            success_rate_increase=payload.success_rate_increase,
            refund_rate_reduction=payload.refund_rate_reduction,
            churn_rate_reduction=payload.churn_rate_reduction,
            retention_increase=payload.retention_increase,
            volume_growth=payload.volume_growth
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/digital-twin/{merchant_id}")
def get_digital_twin_simulation(
    merchant_id: str,
    success_rate: Optional[float] = Query(None, description="Target simulated success rate"),
    refund_rate: Optional[float] = Query(None, description="Target simulated refund rate"),
    volume_growth: float = Query(0.0, description="Volume growth percentage")
):
    """
    GET endpoint for interactive Digital Twin simulation.
    """
    try:
        return digital_twin_agent(
            merchant_id=merchant_id,
            simulated_success_rate=success_rate,
            simulated_refund_rate=refund_rate,
            volume_growth=volume_growth
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Digital Twin simulation error: {str(e)}")