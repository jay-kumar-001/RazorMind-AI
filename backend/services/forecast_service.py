from typing import Dict, Any, List
import hashlib
import numpy as np
from sklearn.linear_model import LinearRegression

from backend.services.ttl_cache import forecast_cache
from backend.services.merchant_context import snapshot_metrics, data_confidence


class ForecastService:
    @staticmethod
    def generate_forecast(merchant: Any, months_ahead: int = 3) -> List[Dict[str, Any]]:
        mid = str(getattr(merchant, "merchant_id", "unknown"))
        cache_key = f"{mid}:{months_ahead}"
        cached = forecast_cache.get(cache_key)
        if cached is not None:
            return cached

        base_revenue = float(getattr(merchant, "total_revenue", 0.0) or 0.0)
        health_score = float(getattr(merchant, "merchant_health_score", 0.0) or 0.0)
        success_rate = float(getattr(merchant, "success_rate", 0.0) or 0.0)
        refund_rate = float(getattr(merchant, "refund_rate", 0.0) or 0.0)
        category = str(getattr(merchant, "category", "E-Commerce") or "E-Commerce")

        monthly_drift = (health_score - 60.0) * 0.0015 + (success_rate - 90.0) * 0.001 - (refund_rate - 2.0) * 0.0008

        seed = int(hashlib.md5(mid.encode("utf-8")).hexdigest()[:8], 16) % (2**31)
        rng = np.random.default_rng(seed)

        history_x = np.arange(1, 13).reshape(-1, 1)
        history_y = []
        rev = base_revenue
        for i in range(11, -1, -1):
            step = 1.0 + monthly_drift
            rev = rev / max(step, 0.01)
            jitter = 1.0 + (rng.normal(0, 0.012) if i > 0 else 0.0)
            history_y.insert(0, max(0.0, rev * jitter))
        history_y[-1] = base_revenue

        model = LinearRegression()
        model.fit(history_x, np.array(history_y))
        residuals = np.array(history_y) - model.predict(history_x)
        residual_std = float(np.std(residuals)) if len(residuals) else base_revenue * 0.06

        forecasts: List[Dict[str, Any]] = []
        for i in range(1, months_ahead + 1):
            x = np.array([[12 + i]])
            projected = float(model.predict(x)[0])
            band = residual_std * 1.96 * (1.0 + 0.18 * (i - 1))
            lower = max(0.0, projected - band)
            upper = projected + band
            growth_pct = round(((projected - base_revenue) / max(base_revenue, 1.0)) * 100.0, 2)
            forecasts.append({
                "forecast_month": f"Month+{i}",
                "predicted_revenue": round(projected, 2),
                "confidence_lower": round(lower, 2),
                "confidence_upper": round(upper, 2),
                "growth_percent": growth_pct,
                "trend_slope": round(float(model.coef_[0]) / max(base_revenue, 1.0) * 100.0, 3),
                "model": "LinearRegression",
                "method": "KPI-trajectory OLS (12 reconstructed months + health/auth drift)",
                "category": category,
            })

        conf = data_confidence(merchant)
        for f in forecasts:
            f["confidence_score"] = conf
            f["feature_importance"] = {
                "merchant_health_score": round(abs(health_score - 60.0) / 40.0, 3),
                "success_rate": round(abs(success_rate - 90.0) / 15.0, 3),
                "refund_rate": round(abs(refund_rate - 2.0) / 4.0, 3),
            }
            f["explanation"] = (
                f"OLS slope {float(model.coef_[0]):,.0f} INR/month from reconstructed history. "
                f"95% band uses residual σ={residual_std:,.0f} (not a Prophet interval)."
            )
            f["source_metrics"] = snapshot_metrics(merchant)

        forecast_cache.set(cache_key, forecasts)
        return forecasts


forecast_service = ForecastService()
