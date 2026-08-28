from typing import Dict, Any, List
import math

class RiskService:
    @staticmethod
    def calculate_merchant_risk(merchant: Any) -> Dict[str, Any]:
        """
        Calculates a multi-factor risk assessment for a merchant.
        """
        success_rate = float(getattr(merchant, "success_rate", 92.0) or 92.0)
        refund_rate = float(getattr(merchant, "refund_rate", 1.5) or 1.5)
        retention_score = float(getattr(merchant, "retention_score", 30.0) or 30.0)
        total_revenue = float(getattr(merchant, "total_revenue", 100000.0) or 100000.0)
        health_score = float(getattr(merchant, "merchant_health_score", 75.0) or 75.0)
        total_transactions = int(getattr(merchant, "total_transactions", 500) or 500)

        # 1. Failure Rate Risk (Weight: 35%)
        # Benchmarks: >=95% is 0 risk, <=80% is 100 risk
        failure_rate = max(0.0, 100.0 - success_rate)
        if success_rate >= 95.0:
            failure_risk = 0.0
        elif success_rate <= 80.0:
            failure_risk = 100.0
        else:
            failure_risk = ((95.0 - success_rate) / 15.0) * 100.0

        # 2. Refund Rate Risk (Weight: 25%)
        # Benchmarks: <=1.0% is 0 risk, >=5.0% is 100 risk
        if refund_rate <= 1.0:
            refund_risk = 0.0
        elif refund_rate >= 5.0:
            refund_risk = 100.0
        else:
            refund_risk = ((refund_rate - 1.0) / 4.0) * 100.0

        # 3. Retention Risk (Weight: 20%)
        # Benchmarks: >=40% repeat is 0 risk, <=10% is 100 risk
        if retention_score >= 40.0:
            retention_risk = 0.0
        elif retention_score <= 10.0:
            retention_risk = 100.0
        else:
            retention_risk = ((40.0 - retention_score) / 30.0) * 100.0

        # 4. Volume / Stability Risk (Weight: 20%)
        if health_score >= 80.0:
            health_risk = 0.0
        elif health_score <= 40.0:
            health_risk = 100.0
        else:
            health_risk = ((80.0 - health_score) / 40.0) * 100.0

        # Composite Weighted Risk Score (0 - 100)
        composite_risk = (
            failure_risk * 0.35 +
            refund_risk * 0.25 +
            retention_risk * 0.20 +
            health_risk * 0.20
        )
        composite_risk = round(max(0.0, min(100.0, composite_risk)), 2)

        # Risk Classification
        if composite_risk < 25.0:
            risk_level = "LOW"
            severity = "Normal"
        elif composite_risk < 55.0:
            risk_level = "MEDIUM"
            severity = "Moderate"
        elif composite_risk < 80.0:
            risk_level = "HIGH"
            severity = "Severe"
        else:
            risk_level = "CRITICAL"
            severity = "Immediate Action Required"

        # Diagnostic Risk Factors & Anomaly Detection
        risk_factors: List[str] = []
        recommendations: List[str] = []

        if success_rate < 90.0:
            risk_factors.append(f"Suboptimal payment success rate ({success_rate:.1f}% vs 94.0% benchmark)")
            recommendations.append("Activate Dynamic Gateway Routing with AI fallback")
            recommendations.append("Enable Smart Retry Engine for soft bank declines")
        elif success_rate < 93.0:
            risk_factors.append(f"Minor authorization dropoff ({success_rate:.1f}%)")
            recommendations.append("Optimize card network tokenization and 3DS challenge flow")

        if refund_rate > 3.0:
            risk_factors.append(f"Elevated refund rate ({refund_rate:.1f}% exceeds 2.0% threshold)")
            recommendations.append("Audit merchant fulfillment latency and return policy friction")
            recommendations.append("Implement pre-chargeback dispute alert integrations (Ethoca/Verifi)")
        elif refund_rate > 2.0:
            risk_factors.append(f"Moderate refund velocity ({refund_rate:.1f}%)")
            recommendations.append("Enforce multi-factor verification on high-ticket SKUs")

        if retention_score < 20.0:
            risk_factors.append(f"Low repeat customer retention ({retention_score:.1f}%)")
            recommendations.append("Deploy merchant automated loyalty and re-engagement workflows")

        if total_revenue < 50000.0:
            risk_factors.append("Low monthly throughput with high revenue variance")
            recommendations.append("Accelerate merchant transaction volume via instant settlement incentives")

        if not risk_factors:
            risk_factors.append("Healthy merchant profile: all operational KPIs within prime parameters")
            recommendations.append("Eligible for line of credit expansion and lower interchange tier")

        # Unique recommendations
        recommendations = list(dict.fromkeys(recommendations))

        # Explainability summary
        explanation = (
            f"Merchant exhibits an aggregate risk score of {composite_risk}/100 categorized as {risk_level}. "
            f"Key drivers include authorization performance ({success_rate:.1f}% success rate) "
            f"and chargeback/refund volume ({refund_rate:.1f}% refund rate). "
            f"{'Primary exposure stems from payment routing inefficiencies.' if failure_risk > 40 else 'Operational signals remain steady.'}"
        )

        confidence_score = round(90.0 + min(9.0, total_transactions / 200.0), 1)

        return {
            "merchant_id": getattr(merchant, "merchant_id", "Unknown"),
            "risk_score": composite_risk,
            "risk_level": risk_level,
            "severity": severity,
            "confidence_score": confidence_score,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "factor_breakdown": {
                "failure_risk": round(failure_risk, 2),
                "refund_risk": round(refund_risk, 2),
                "retention_risk": round(retention_risk, 2),
                "health_risk": round(health_risk, 2)
            },
            "explanation": explanation
        }

risk_service = RiskService()
