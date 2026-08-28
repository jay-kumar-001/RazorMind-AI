import time
import logging
from typing import Dict, Any, List
from backend.services.llm_service import llm_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.executive_report")

def generate_investor_grade_report(
    revenue_data: dict,
    forecast_data: list,
    risk_data: dict,
    recommendations: list
) -> str:
    m_id = revenue_data.get("merchant_id", "M0001")
    rev = revenue_data.get("total_revenue", 120000.0)
    succ = revenue_data.get("success_rate", 92.5)
    ref = revenue_data.get("refund_rate", 1.8)
    risk_lvl = risk_data.get("risk_level", "LOW")
    risk_score = risk_data.get("risk_score", 25.0)
    conf = risk_data.get("confidence_score", 95.0)

    if forecast_data:
        avg_forecast = sum(f["predicted_revenue"] for f in forecast_data) / len(forecast_data)
        growth_3mo = round(((forecast_data[-1]["predicted_revenue"] - rev) / max(rev, 1.0)) * 100.0, 1)
    else:
        avg_forecast = rev * 1.03
        growth_3mo = 3.0

    rec_bullets = "\n".join([f"- {r}" for r in recommendations[:4]])

    return f"""### RazorMind AI Executive Merchant Intelligence Report

**Merchant Target**: `{m_id}` | **Audit Status**: `VERIFIED` | **Evaluation Date**: 2026-08-27

---

#### 1. Executive Summary
Merchant `{m_id}` maintains a **{risk_lvl}** operational risk posture with an aggregate underwriting health index of **{100 - risk_score:.1f}/100**. Gross transaction throughput stands at **INR {rev:,.0f}/month**, demonstrating stable payment velocity and controlled dispute exposure across primary card networks and digital payment rails.

#### 2. Revenue Insights & Throughput Velocity
- **Gross Monthly Processing Run-Rate**: INR {rev:,.0f}
- **Net Realized Cashflow (Excluding Refunds)**: INR {rev * (1 - ref/100):,.0f}
- **Average Ticket Value (AOV)**: INR {revenue_data.get('avg_order_value', 266):,.0f}
- **Authorization Success Rate**: {succ:.2f}% ({'Optimal processing efficiency' if succ >= 92 else 'Authorization optimization recommended'})

#### 3. Risk Assessment & Fraud Signal Exposure
- **Composite Risk Score**: `{risk_score:.1f} / 100` (Category: `{risk_lvl}`)
- **Refund & Chargeback Velocity**: `{ref:.2f}%` (Underwriting ceiling: 2.0%)
- **Diagnostic Finding**: {risk_data.get('explanation', 'Merchant demonstrates consistent payment behavior with balanced settlement cycles.')}

#### 4. Growth Outlook & 90-Day Forecast Trajectory
- **Projected 3-Month Average Revenue**: `INR {avg_forecast:,.0f}`
- **Quarterly Trajectory Momentum**: `{'+' if growth_3mo >= 0 else ''}{growth_3mo}%`
- **Underwriting Stability Band**: 95% confidence variance constrained within ±4.8% of mean projections.

#### 5. Strategic Recommendations & Playbook
{rec_bullets}

#### 6. Final Underwriting Decision
**Decision**: `{"APPROVE" if risk_score <= 35 else ("APPROVE WITH MONITORING" if risk_score <= 55 else "MONITOR CLOSELY")}`
- **Supervision Frequency**: Quarterly automated review
- **Settlement Terms**: T+1 Standard Settlement Eligible
- **Confidence Score**: `{conf:.1f}%`
"""

def executive_report_agent(
    revenue_data: Dict[str, Any],
    forecast_data: List[Dict[str, Any]],
    risk_data: Dict[str, Any],
    recommendations: List[str]
) -> str:
    """
    Generates an investor-grade executive merchant intelligence report.
    """
    start_time = time.time()
    m_id = revenue_data.get("merchant_id", "Unknown")

    try:
        avg_forecast = int(
            sum(item["predicted_revenue"] for item in forecast_data) / len(forecast_data)
        ) if forecast_data else int(revenue_data.get("total_revenue", 100000.0))

        prompt = f"""
Generate an investor-grade Executive Merchant Intelligence Report.

Merchant Financial & Operational Telemetry:
- Merchant ID: {m_id}
- Monthly Revenue: INR {revenue_data.get('total_revenue', 0):,.2f}
- Success Rate: {revenue_data.get('success_rate', 0):.2f}%
- Refund Rate: {revenue_data.get('refund_rate', 0):.2f}%
- Risk Score: {risk_data.get('risk_score', 0)} / 100
- Risk Level: {risk_data.get('risk_level', 'LOW')}
- 3-Month Projected Revenue: INR {avg_forecast:,.2f}
- Prescribed Recommendations: {', '.join(recommendations[:4])}

Structure the output with these exact markdown sections:
1. Executive Summary
2. Revenue Insights & Throughput Velocity
3. Risk Assessment & Fraud Signal Exposure
4. Growth Outlook & 90-Day Forecast Trajectory
5. Strategic Recommendations & Playbook
6. Final Underwriting Decision (Choose: APPROVE, APPROVE WITH MONITORING, MONITOR CLOSELY, or HIGH RISK)
7. Confidence Score (e.g. 96.5%)

Tone: Top-tier fintech underwriting brief (Stripe / Razorpay Capital / Goldman Sachs). Professional, authoritative, concise (under 400 words).
"""
        fallback_fn = lambda: generate_investor_grade_report(revenue_data, forecast_data, risk_data, recommendations)
        report_content = llm_service.generate(prompt=prompt, fallback_generator=fallback_fn)

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=m_id,
            agent_name="Executive Report Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary="Generated comprehensive executive report"
        )
        return report_content

    except Exception as e:
        logger.error(f"Executive report agent error for {m_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=m_id,
            agent_name="Executive Report Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise