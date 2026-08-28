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
    Returns statistical & trend-based revenue forecast with 95% confidence intervals.
    """
    # Check if existing in DB first
    forecasts = (
        db.query(RevenueForecast)
        .filter(RevenueForecast.merchant_id == merchant_id)
        .order_by(RevenueForecast.id.asc())
        .limit(months)
        .all()
    )

    if forecasts and len(forecasts) >= months:
        return [
            {
                "forecast_month": f.forecast_month,
                "predicted_revenue": f.predicted_revenue,
                "confidence_lower": f.confidence_lower,
                "confidence_upper": f.confidence_upper,
                "trend_slope": f.trend_slope,
                "method": "stored_revenue_forecasts",
            }
            for f in forecasts
        ]

    # Generate dynamically on the fly
    try:
        results = forecast_agent(merchant_id=merchant_id, months_ahead=months)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast calculation failed: {str(e)}")