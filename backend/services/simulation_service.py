from typing import Dict, Any, Optional
from backend.services.risk_service import risk_service
from backend.services.forecast_service import forecast_service

class MockMerchantSnapshot:
    """Snapshot container for simulation calculation."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class SimulationService:
    @staticmethod
    def run_simulation(
        merchant: Any,
        success_rate_delta: float = 0.0,
        refund_rate_delta: float = 0.0,
        churn_rate_delta: float = 0.0,
        retention_delta: float = 0.0,
        volume_growth_delta: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes a high-fidelity Digital Twin what-if simulation on a merchant.
        """
        base_revenue = float(getattr(merchant, "total_revenue", 100000.0) or 100000.0)
        base_success = float(getattr(merchant, "success_rate", 92.0) or 92.0)
        base_refund = float(getattr(merchant, "refund_rate", 2.0) or 2.0)
        base_retention = float(getattr(merchant, "retention_score", 30.0) or 30.0)
        base_health = float(getattr(merchant, "merchant_health_score", 75.0) or 75.0)
        category = str(getattr(merchant, "category", "E-Commerce") or "E-Commerce")
        total_tx = int(getattr(merchant, "total_transactions", 500) or 500)

        # Baseline Risk Assessment
        baseline_risk = risk_service.calculate_merchant_risk(merchant)

        # Apply Simulated Delta Shifts with Realistic Boundaries
        sim_success = max(50.0, min(99.9, base_success + success_rate_delta))
        sim_refund = max(0.0, min(30.0, base_refund + refund_rate_delta))
        sim_retention = max(5.0, min(95.0, base_retention + retention_delta))

        # Direct authorization lift impact on gross captured volume
        # If success rate changes from 90% to 95%, revenue scales by (95 / 90)
        success_multiplier = (sim_success / max(base_success, 1.0))
        
        # Refund change saves or drains cashflow
        # Reduction in refunds directly recovers lost sales
        refund_delta_impact = -(sim_refund - base_refund) / 100.0
        
        # Churn reduction boosts repeat transaction baseline
        churn_recovery = -(churn_rate_delta / 100.0) * 0.4
        
        # Retention increase compounds customer lifetime value
        retention_lift = (retention_delta / 100.0) * 0.3
        
        # Exogenous volume growth percentage
        volume_mult = 1.0 + (volume_growth_delta / 100.0)

        combined_revenue_multiplier = (
            success_multiplier *
            (1.0 + refund_delta_impact + churn_recovery + retention_lift) *
            volume_mult
        )

        sim_revenue = round(base_revenue * combined_revenue_multiplier, 2)
        revenue_diff = round(sim_revenue - base_revenue, 2)
        revenue_growth_pct = round(((sim_revenue - base_revenue) / max(base_revenue, 1.0)) * 100.0, 2)

        # Health score dynamic rebalancing
        health_shift = (
            (sim_success - base_success) * 0.7 +
            -(sim_refund - base_refund) * 2.5 +
            (sim_retention - base_retention) * 0.4 +
            (volume_growth_delta) * 0.15 -
            (churn_rate_delta) * 0.3
        )
        sim_health = round(max(5.0, min(100.0, base_health + health_shift)), 2)

        # Create simulated snapshot to compute updated risk & forecast
        sim_snapshot = MockMerchantSnapshot(
            merchant_id=getattr(merchant, "merchant_id", "Simulated"),
            total_revenue=sim_revenue,
            success_rate=sim_success,
            refund_rate=sim_refund,
            retention_score=sim_retention,
            merchant_health_score=sim_health,
            category=category,
            total_transactions=int(total_tx * volume_mult)
        )

        sim_risk = risk_service.calculate_merchant_risk(sim_snapshot)
        sim_forecast = forecast_service.generate_forecast(sim_snapshot, months_ahead=3)
        baseline_forecast = forecast_service.generate_forecast(merchant, months_ahead=3)

        # Status categorization
        if sim_health >= 78.0:
            sim_status = "Healthy (Prime Tier)"
        elif sim_health >= 58.0:
            sim_status = "Moderate Risk (Watchlist)"
        else:
            sim_status = "Critical (Intervention Required)"

        # Business Impact Insights
        impact_summary = []
        if revenue_diff > 0:
            impact_summary.append(f"Projected annualized revenue lift of INR {revenue_diff * 12:,.0f} (+{revenue_growth_pct}%).")
        elif revenue_diff < 0:
            impact_summary.append(f"Risk exposure indicates potential annual shrinkage of INR {abs(revenue_diff) * 12:,.0f}.")

        risk_diff = round(sim_risk["risk_score"] - baseline_risk["risk_score"], 2)
        if risk_diff < 0:
            impact_summary.append(f"Risk score decreased by {abs(risk_diff):.1f} points, improving merchant underwriting tier.")
        elif risk_diff > 0:
            impact_summary.append(f"Risk profile elevated by +{risk_diff:.1f} points.")

        return {
            "merchant_id": getattr(merchant, "merchant_id", "Unknown"),
            "inputs": {
                "success_rate_delta": success_rate_delta,
                "refund_rate_delta": refund_rate_delta,
                "churn_rate_delta": churn_rate_delta,
                "retention_delta": retention_delta,
                "volume_growth_delta": volume_growth_delta
            },
            "baseline": {
                "revenue": base_revenue,
                "health_score": base_health,
                "risk_score": baseline_risk["risk_score"],
                "risk_level": baseline_risk["risk_level"],
                "success_rate": base_success,
                "refund_rate": base_refund,
                "forecast": baseline_forecast
            },
            "simulated": {
                "revenue": sim_revenue,
                "revenue_difference": revenue_diff,
                "revenue_growth_percent": revenue_growth_pct,
                "health_score": sim_health,
                "status": sim_status,
                "risk_score": sim_risk["risk_score"],
                "risk_level": sim_risk["risk_level"],
                "success_rate": sim_success,
                "refund_rate": sim_refund,
                "forecast": sim_forecast
            },
            "impact_summary": impact_summary
        }

simulation_service = SimulationService()
