import time
import logging
from typing import Dict, Any, List
from agents.revenue_agent import get_merchant_data
from backend.services.risk_service import risk_service
from backend.services.llm_service import llm_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.action_plan")

def generate_dynamic_action_plan(merchant_data: dict, risk_data: dict, recommendations: List[str]) -> str:
    m_id = merchant_data.get("merchant_id", "Merchant")
    health = merchant_data.get("merchant_health_score", 75.0)
    succ = merchant_data.get("success_rate", 92.0)
    ref = merchant_data.get("refund_rate", 1.8)
    risk_lvl = risk_data.get("risk_level", "LOW")

    primary_rec = recommendations[0] if recommendations else "Optimize Gateway Failover Rules"
    secondary_rec = recommendations[1] if len(recommendations) > 1 else "Audit Chargeback Exposure"

    return f"""### 30-Day Tactical Merchant Action Plan: {m_id}

**Risk Posture**: `{risk_lvl}` | **Health Baseline**: `{health:.1f}/100` | **Success Rate**: `{succ:.1f}%`

#### Week 1: Diagnostic & Immediate Routing Optimization
- Audit top failure response codes (`Do Not Honor`, `Insufficient Funds`, `3DS Timeout`).
- **Action**: {primary_rec}.
- Implement adaptive card routing across primary and backup banking acquirers.
- **Milestone**: Recover +1.5% in soft bank declines within 7 days.

#### Week 2: Refund & Friction Elimination
- Review return/refund dispute velocity (Current: {ref:.1f}%).
- **Action**: {secondary_rec}.
- Integrate real-time pre-chargeback dispute alert webhooks (Ethoca/Verifi) to intercept inquiries.
- **Milestone**: Reduce refund processing turnaround time to < 24 hours.

#### Week 3: Customer Retention & Checkout Acceleration
- Implement tokenized 1-click checkout for repeat customers (Retention index: {merchant_data.get('retention_score', 25):.1f}%).
- Deploy automated SMS/WhatsApp order status notifications to prevent buyer remorse.
- **Milestone**: Increase repeat buyer checkout completion by +2.2%.

#### Week 4: Risk Calibration & Performance Review
- Re-evaluate composite risk scorecard and underwriter monitoring parameters.
- Benchmark authorization metrics against 30-day historical baseline.
- Conduct executive sign-off for line-of-credit expansion.
- **Milestone**: Finalize risk tier re-certification and confirm expected monthly revenue lift.

---
**Expected 30-Day Business Outcome**:
- **Projected Revenue Lift**: `+INR {round(merchant_data.get('total_revenue', 100000) * 0.045, 0):,}` per month.
- **Target Authorization Rate**: `+{min(99.0, succ + 2.5):.1f}%`.
- **Target Risk Reduction**: `-8.5 points` on composite risk index.
"""

def action_plan_agent(
    merchant_id: str,
    risk_level: str = "MEDIUM",
    recommendations: List[str] = None
) -> Dict[str, Any]:
    """
    Generates a personalized, tactical 30-day action plan tailored to merchant metrics and risk tier.
    """
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            class DefaultMerchant:
                merchant_id = merchant_id
                merchant_name = merchant_id
                total_revenue = 120000.0
                success_rate = 92.5
                refund_rate = 1.8
                retention_score = 30.0
                merchant_health_score = 75.0
            merchant = DefaultMerchant()

        risk_data = risk_service.calculate_merchant_risk(merchant)
        recs = recommendations or risk_data.get("recommendations", [])

        merchant_dict = {
            "merchant_id": merchant_id,
            "total_revenue": float(getattr(merchant, "total_revenue", 120000.0) or 120000.0),
            "success_rate": float(getattr(merchant, "success_rate", 92.5) or 92.5),
            "refund_rate": float(getattr(merchant, "refund_rate", 1.8) or 1.8),
            "retention_score": float(getattr(merchant, "retention_score", 30.0) or 30.0),
            "merchant_health_score": float(getattr(merchant, "merchant_health_score", 75.0) or 75.0)
        }

        prompt = f"""
You are an elite Fintech Merchant Growth Consultant & Risk Underwriter.

Generate a comprehensive 30-Day Merchant Action Plan for Merchant {merchant_id}.

Context:
- Revenue: INR {merchant_dict['total_revenue']:,.2f}
- Success Rate: {merchant_dict['success_rate']:.2f}%
- Refund Rate: {merchant_dict['refund_rate']:.2f}%
- Health Score: {merchant_dict['merchant_health_score']:.1f}/100
- Risk Level: {risk_data['risk_level']} (Score: {risk_data['risk_score']})
- Priority Recommendations: {', '.join(recs[:3])}

Structure the plan strictly as:
- Executive Overview
- Week 1: Diagnostic & Immediate Routing Optimization
- Week 2: Refund & Friction Elimination
- Week 3: Customer Retention & Checkout Acceleration
- Week 4: Risk Calibration & Performance Review
- Expected 30-Day Business Outcome (Revenue lift and risk shift)

Be highly quantitative and specific to these metrics. Under 350 words.
"""
        fallback_fn = lambda: generate_dynamic_action_plan(merchant_dict, risk_data, recs)
        plan_content = llm_service.generate(prompt=prompt, fallback_generator=fallback_fn)

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Action Plan Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary="Generated 30-Day tactical roadmap"
        )

        return {
            "merchant_id": merchant_id,
            "action_plan": plan_content,
            "risk_level": risk_data["risk_level"],
            "expected_revenue_impact": round(merchant_dict["total_revenue"] * 0.045, 2)
        }

    except Exception as e:
        logger.error(f"Action plan agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Action Plan Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise