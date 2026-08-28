from typing import Dict, Any, List

from backend.services.ttl_cache import risk_cache
from backend.services.merchant_context import snapshot_metrics, data_confidence


class RiskService:
    @staticmethod
    def calculate_merchant_risk(merchant: Any) -> Dict[str, Any]:
        mid = str(getattr(merchant, "merchant_id", "unknown"))
        cache_key = (
            f"{mid}:{getattr(merchant, 'success_rate', 0)}:"
            f"{getattr(merchant, 'refund_rate', 0)}:{getattr(merchant, 'merchant_health_score', 0)}:"
            f"{getattr(merchant, 'retention_score', 0)}"
        )
        cached = risk_cache.get(cache_key)
        if cached is not None:
            return cached

        success_rate = float(getattr(merchant, "success_rate", 0.0) or 0.0)
        refund_rate = float(getattr(merchant, "refund_rate", 0.0) or 0.0)
        chargeback_rate = float(getattr(merchant, "chargeback_rate", 0.0) or 0.0)
        retention_score = float(getattr(merchant, "retention_score", 0.0) or 0.0)
        total_revenue = float(getattr(merchant, "total_revenue", 0.0) or 0.0)
        health_score = float(getattr(merchant, "merchant_health_score", 0.0) or 0.0)
        total_transactions = int(getattr(merchant, "total_transactions", 0) or 0)

        if success_rate >= 95.0:
            failure_risk = 0.0
        elif success_rate <= 80.0:
            failure_risk = 100.0
        else:
            failure_risk = ((95.0 - success_rate) / 15.0) * 100.0

        if refund_rate <= 1.0:
            refund_risk = 0.0
        elif refund_rate >= 5.0:
            refund_risk = 100.0
        else:
            refund_risk = ((refund_rate - 1.0) / 4.0) * 100.0

        if chargeback_rate <= 0.5:
            cb_risk = 0.0
        elif chargeback_rate >= 3.0:
            cb_risk = 100.0
        else:
            cb_risk = ((chargeback_rate - 0.5) / 2.5) * 100.0

        if retention_score >= 40.0:
            retention_risk = 0.0
        elif retention_score <= 10.0:
            retention_risk = 100.0
        else:
            retention_risk = ((40.0 - retention_score) / 30.0) * 100.0

        if health_score >= 80.0:
            health_risk = 0.0
        elif health_score <= 40.0:
            health_risk = 100.0
        else:
            health_risk = ((80.0 - health_score) / 40.0) * 100.0

        composite_risk = (
            failure_risk * 0.30 +
            refund_risk * 0.22 +
            cb_risk * 0.13 +
            retention_risk * 0.18 +
            health_risk * 0.17
        )
        composite_risk = round(max(0.0, min(100.0, composite_risk)), 2)

        if composite_risk < 25.0:
            risk_level, severity = "LOW", "Normal"
        elif composite_risk < 55.0:
            risk_level, severity = "MEDIUM", "Moderate"
        elif composite_risk < 80.0:
            risk_level, severity = "HIGH", "Severe"
        else:
            risk_level, severity = "CRITICAL", "Immediate Action Required"

        risk_factors: List[str] = []
        recommendations: List[str] = []

        if success_rate < 90.0:
            gap = round(94.0 - success_rate, 1)
            est_loss = round(total_revenue * max(gap, 0) / 100.0 * 0.85, 0)
            risk_factors.append(
                f"Authorization gap: {success_rate:.1f}% vs 94% benchmark (est. INR {est_loss:,.0f}/mo leakage)"
            )
            recommendations.append(f"Prioritize smart retry + backup acquirer routing to close {gap:.1f}pp auth gap")
        elif success_rate < 93.0:
            risk_factors.append(f"Minor authorization dropoff at {success_rate:.1f}%")
            recommendations.append("Tune 3DS exemption and tokenized retry on this merchant's top decline codes")

        if refund_rate > 3.0:
            risk_factors.append(f"Refund velocity {refund_rate:.1f}% exceeds 2.0% underwriting ceiling")
            recommendations.append("Audit SKU-level returns and enable Ethoca/Verifi pre-dispute alerts")
        elif refund_rate > 2.0:
            risk_factors.append(f"Moderate refund rate {refund_rate:.1f}%")
            recommendations.append("Add high-AOV verification and clearer cancellation SLAs")

        if chargeback_rate > 1.0:
            risk_factors.append(f"Chargeback rate {chargeback_rate:.2f}% above 1.0% watch threshold")
            recommendations.append("Tighten descriptor clarity and representment playbook")

        if retention_score < 20.0:
            risk_factors.append(f"Weak repeat-customer index ({retention_score:.1f})")
            recommendations.append("Tokenized checkout + win-back campaign on lapsed buyers")

        if total_revenue < 50000.0:
            risk_factors.append("Low throughput increases score variance")
            recommendations.append("Volume incentives only after auth/refund stabilize")

        if not risk_factors:
            risk_factors.append(
                f"KPIs inside prime band (auth {success_rate:.1f}%, refund {refund_rate:.1f}%, health {health_score:.1f})"
            )
            recommendations.append("Eligible for limit expansion; keep quarterly automated review")

        recommendations = list(dict.fromkeys(recommendations))
        weights = {
            "failure_risk": 0.30,
            "refund_risk": 0.22,
            "chargeback_risk": 0.13,
            "retention_risk": 0.18,
            "health_risk": 0.17,
        }
        breakdown = {
            "failure_risk": round(failure_risk, 2),
            "refund_risk": round(refund_risk, 2),
            "chargeback_risk": round(cb_risk, 2),
            "retention_risk": round(retention_risk, 2),
            "health_risk": round(health_risk, 2),
        }
        top_driver = max(breakdown, key=breakdown.get)
        explanation = (
            f"Weighted score {composite_risk}/100 ({risk_level}). "
            f"Largest contributor: {top_driver.replace('_', ' ')} = {breakdown[top_driver]}. "
            f"Auth {success_rate:.1f}%, refund {refund_rate:.1f}%, chargeback {chargeback_rate:.2f}%."
        )

        result = {
            "merchant_id": getattr(merchant, "merchant_id", "Unknown"),
            "risk_score": composite_risk,
            "risk_level": risk_level,
            "severity": severity,
            "confidence_score": data_confidence(merchant),
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "factor_breakdown": breakdown,
            "feature_importance": weights,
            "top_driver": top_driver,
            "explanation": explanation,
            "reasoning_summary": explanation,
            "source_metrics": snapshot_metrics(merchant),
            "model": "weighted_scorecard_v2",
        }
        risk_cache.set(cache_key, result)
        return result


risk_service = RiskService()
