import time
import logging
from typing import Dict, Any, List
from agents.revenue_agent import get_merchant_data
from backend.services.risk_service import risk_service
from backend.services.llm_service import llm_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.action_plan")


def _auth_gap_lift(merchant_data: dict) -> float:
    succ = float(merchant_data.get("success_rate") or 0.0)
    rev = float(merchant_data.get("total_revenue") or 0.0)
    gap = max(0.0, 94.0 - succ)
    return round(rev * (gap / 100.0) * 0.6, 2)


def generate_dynamic_action_plan(merchant_data: dict, risk_data: dict, recommendations: List[str]) -> str:
    m_id = merchant_data.get("merchant_id", "Merchant")
    health = float(merchant_data.get("merchant_health_score") or 0.0)
    succ = float(merchant_data.get("success_rate") or 0.0)
    ref = float(merchant_data.get("refund_rate") or 0.0)
    risk_lvl = risk_data.get("risk_level", "LOW")
    primary_rec = recommendations[0] if recommendations else "Optimize gateway failover for this merchant's decline mix"
    secondary_rec = recommendations[1] if len(recommendations) > 1 else "Audit refund SKUs against AOV"
    auth_gap = round(max(0.0, 94.0 - succ), 2)
    lift = _auth_gap_lift(merchant_data)
    risk_cut = round(min(12.0, auth_gap * 0.8 + max(0, ref - 2.0) * 1.2), 1)

    return f"""### 30-Day Tactical Merchant Action Plan: {m_id}

**Risk Posture**: `{risk_lvl}` | **Health Baseline**: `{health:.1f}/100` | **Success Rate**: `{succ:.1f}%`

#### Week 1: Diagnostic & Immediate Routing Optimization
- Audit top failure response codes for this MID.
- **Action**: {primary_rec}.
- **Milestone**: Close ~{min(auth_gap, 1.5):.1f}pp of the {auth_gap:.1f}pp auth gap (Expected Lift: +INR {lift:,.2f}/mo).

#### Week 2: Refund & Friction Elimination
- Current refund velocity: {ref:.1f}%.
- **Action**: {secondary_rec}.
- **Milestone**: Target refund ≤ {max(1.5, ref - 0.4):.1f}%.

#### Week 3: Customer Retention & Checkout Acceleration
- Retention index: {float(merchant_data.get('retention_score') or 0):.1f}%.
- Tokenized checkout + post-purchase notifications.

#### Week 4: Risk Recalibration
- Re-run the same weighted scorecard vs day-0 baseline.
- Confirm whether the merchant can move underwriting tier.

---
**Expected 30-Day Business Outcome** (auth-gap capture, not a flat multiplier):
- **Projected Revenue Lift**: `+INR {lift:,.2f}` / month
- **Target Authorization Rate**: `{min(99.0, succ + min(2.5, auth_gap)):.1f}%`
- **Target Risk Reduction**: `~{risk_cut:.1f} points` if Weeks 1–2 land
"""


def action_plan_agent(
    merchant_id: str,
    risk_level: str = "MEDIUM",
    recommendations: List[str] = None,
    use_llm: bool = True,
) -> Dict[str, Any]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")

        risk_data = risk_service.calculate_merchant_risk(merchant)
        recs = recommendations or risk_data.get("recommendations", [])
        merchant_dict = {
            "merchant_id": merchant_id,
            "total_revenue": float(getattr(merchant, "total_revenue", 0.0) or 0.0),
            "success_rate": float(getattr(merchant, "success_rate", 0.0) or 0.0),
            "refund_rate": float(getattr(merchant, "refund_rate", 0.0) or 0.0),
            "retention_score": float(getattr(merchant, "retention_score", 0.0) or 0.0),
            "merchant_health_score": float(getattr(merchant, "merchant_health_score", 0.0) or 0.0),
        }
        lift = _auth_gap_lift(merchant_dict)
        fallback_fn = lambda: generate_dynamic_action_plan(merchant_dict, risk_data, recs)
        if use_llm:
            prompt = f"""Write a 30-day tactical merchant action plan for merchant {merchant_id}.
Revenue INR {merchant_dict['total_revenue']:,.0f}, auth {merchant_dict['success_rate']:.2f}%, refund {merchant_dict['refund_rate']:.2f}%, health {merchant_dict['merchant_health_score']:.1f}, risk {risk_data['risk_level']} ({risk_data['risk_score']}).
Recs: {', '.join(recs[:3])}.
MANDATORY STRUCTURE: Exactly 4 weekly milestones (Week 1, Week 2, Week 3, Week 4) for a 30-day timeline. Do NOT generate any Week 5 or Week 6.
Quantify lift from the {max(0, 94 - merchant_dict['success_rate']):.1f}pp auth gap (est. INR {lift:,.0f}/mo). Under 350 words."""
            plan_content = llm_service.generate(prompt=prompt, fallback_generator=fallback_fn)
        else:
            plan_content = fallback_fn()

        weeks = [
            {"week": "Week 1", "title": "Routing & decline triage", "owner": "Risk Underwriter", "status": "READY", "items": [recs[0]] if recs else ["Audit decline codes", "Enable dynamic retry"]},
            {"week": "Week 2", "title": "Refund & dispute control", "owner": "Payment Eng", "status": "SCHEDULED", "items": [recs[1]] if len(recs) > 1 else ["Refund SKU audit", "Activate pre-dispute alerts"]},
            {"week": "Week 3", "title": "Retention & checkout acceleration", "owner": "Merchant Success", "status": "SCHEDULED", "items": ["Tokenized checkout", "Post-purchase comms", "VIP tier re-engagement"]},
            {"week": "Week 4", "title": "Rescore & underwriting signoff", "owner": "Credit Committee", "status": "PLANNED", "items": ["Re-run risk scorecard", "Tier review", "Adjust GMV authorization limit"]},
        ]
        plan_conf = round(float(risk_data.get("confidence_score") or 75.0) * 0.95, 1)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Action Plan Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=f"Lift estimate INR {lift:,.0f}/mo",
            confidence=plan_conf,
            reasoning=f"Lift from auth gap vs 94% benchmark, not a fixed 4.5% of GMV.",
        )
        return {
            "merchant_id": merchant_id,
            "action_plan": plan_content,
            "risk_level": risk_data["risk_level"],
            "expected_revenue_impact": lift,
            "milestones": weeks,
            "target_risk_tier": "LOW" if risk_data["risk_score"] < 40 else ("MEDIUM" if risk_data["risk_score"] < 65 else "HIGH"),
        }
    except Exception as e:
        logger.error("Action plan agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Action Plan Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
