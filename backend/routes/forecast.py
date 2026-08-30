from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import RevenueForecast, Merchant
from agents.forecast_agent import forecast_agent

router = APIRouter(tags=["Forecast"])

@router.get("/merchant/{merchant_id}/forecast")
def get_forecast(
    merchant_id: str,
    months: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """
    Returns statistical & trend-based revenue forecast with 95% confidence intervals and month-specific velocity.
    """
    try:
        results = forecast_agent(merchant_id=merchant_id, months_ahead=months)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast calculation failed: {str(e)}")