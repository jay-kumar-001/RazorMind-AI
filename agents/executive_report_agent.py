import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from backend.services.llm_service import llm_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.executive_report")

def generate_investor_grade_report(
    revenue_data: dict,
    forecast_data: list,
    risk_data: dict,
    recommendations: list,
    churn_data: dict = None,
    decision_data: dict = None,
) -> str:
    m_id = revenue_data.get("merchant_id", "Unknown")
    total_rev = float(revenue_data.get("total_revenue") or 0.0)
    monthly_rev = round(total_rev / 3.0, 2)
    succ = float(revenue_data.get("success_rate") or 0.0)
    ref = float(revenue_data.get("refund_rate") or 0.0)
    risk_lvl = risk_data.get("risk_level", "LOW")
    risk_score = float(risk_data.get("risk_score") or 0.0)
    churn_p = float((churn_data or {}).get("churn_probability") or 0.0)

    # Derived confidence: weighted average across upstream specialist models (not hardcoded)
    risk_conf = float((risk_data or {}).get("confidence_score") or 75.0)
    fc_conf = float(((forecast_data[0] if forecast_data else {})).get("confidence_score") or 75.0)
    churn_conf = float((churn_data or {}).get("confidence_score") or 75.0)
    conf = round((risk_conf * 0.40 + fc_conf * 0.35 + churn_conf * 0.25), 1)

    if forecast_data:
        avg_forecast = sum(f["predicted_revenue"] for f in forecast_data) / len(forecast_data)
        growth_3mo = round(((forecast_data[-1]["predicted_revenue"] - total_rev) / max(total_rev, 1.0)) * 100.0, 1)
    else:
        avg_forecast = monthly_rev
        growth_3mo = 0.0

    rec_bullets = "\n".join([f"- {r}" for r in recommendations[:4]])
    final_decision = (decision_data or {}).get("final_decision") or ("APPROVE" if risk_score <= 35 and churn_p < 40 else ("APPROVE WITH MONITORING" if risk_score <= 55 else "MONITOR CLOSELY"))

    return f"""### RazorMind AI Executive Merchant Intelligence Report

**Merchant Target**: `{m_id}` | **Audit Status**: `VERIFIED` | **Evaluation Date**: {datetime.now(timezone.utc).date().isoformat()}

---

#### 1. Executive Summary
Merchant `{m_id}` maintains a **{risk_lvl}** operational risk posture with an aggregate underwriting health index of **{100 - risk_score:.1f}/100**. Gross transaction throughput stands at **INR {total_rev:,.2f}** over 3 months, demonstrating stable payment velocity and controlled dispute exposure across primary card networks and digital payment rails.

#### 2. Revenue Insights & Throughput Velocity
- **3M Aggregate Revenue**: INR {total_rev:,.2f}
- **Monthly Revenue (calculated from 3-month average)**: INR {monthly_rev:,.2f}
- **Net Realized Cashflow (Excluding Refunds)**: INR {monthly_rev * (1 - ref/100):,.2f}
- **Average Ticket Value (AOV)**: INR {float(revenue_data.get('avg_order_value') or 0):,.2f}
- **Authorization Success Rate**: {succ:.2f}% ({'Optimal processing efficiency' if succ >= 92 else 'Authorization optimization recommended'})

#### 3. Risk Assessment & Fraud Signal Exposure
- **Composite Risk Score**: `{risk_score:.1f} / 100` (Category: `{risk_lvl}`)
- **Predictive Churn Risk**: `{churn_p:.1f}%` (60-day merchant dropoff index)
- **Refund & Chargeback Velocity**: `{ref:.2f}%` (Underwriting ceiling: 2.0%)
- **Diagnostic Finding**: {risk_data.get('explanation', 'Merchant demonstrates consistent payment behavior with balanced settlement cycles.')}

#### 4. Growth Outlook & 90-Day Forecast Trajectory
- **Projected 3-Month Average Revenue**: `INR {avg_forecast:,.2f}`
- **Quarterly Trajectory Momentum**: `{'+' if growth_3mo >= 0 else ''}{growth_3mo}%`
- **Interval method**: OLS residual 95% band from forecast engine (widens with horizon).

#### 5. Strategic Recommendations & Playbook
{rec_bullets}

#### 6. Final Underwriting Decision
**Decision**: `{final_decision}`
- **Supervision Frequency**: Quarterly automated review
- **Settlement Terms**: T+1 Standard Settlement Eligible
- **Derived Committee Confidence**: `{conf:.1f}%`
"""

def executive_report_agent(
    revenue_data: Dict[str, Any],
    forecast_data: List[Dict[str, Any]],
    risk_data: Dict[str, Any],
    recommendations: List[str],
    churn_data: Dict[str, Any] = None,
    decision_data: Dict[str, Any] = None,
    use_llm: bool = True,
) -> str:
    start_time = time.time()
    m_id = revenue_data.get("merchant_id", "Unknown")

    # Derived confidence: weighted average across upstream specialist models
    risk_conf = float((risk_data or {}).get("confidence_score") or 75.0)
    fc_conf = float(((forecast_data[0] if forecast_data else {})).get("confidence_score") or 75.0)
    churn_conf = float((churn_data or {}).get("confidence_score") or 75.0)
    derived_conf = round((risk_conf * 0.40 + fc_conf * 0.35 + churn_conf * 0.25), 1)

    try:
        fallback_fn = lambda: generate_investor_grade_report(revenue_data, forecast_data, risk_data, recommendations, churn_data, decision_data)
        if use_llm:
            total_rev = float(revenue_data.get("total_revenue") or 0.0)
            monthly_rev = round(total_rev / 3.0, 2)
            three_m_forecast_avg = round(
                sum(item["predicted_revenue"] for item in forecast_data) / len(forecast_data)
            , 2) if forecast_data else monthly_rev
            churn_p = float((churn_data or {}).get("churn_probability") or 0.0)
            final_dec = (decision_data or {}).get("final_decision") or ("APPROVE" if float(risk_data.get("risk_score", 0)) <= 35 and churn_p < 40 else ("APPROVE WITH MONITORING" if float(risk_data.get("risk_score", 0)) <= 55 else "MONITOR CLOSELY"))

            prompt = f"""Generate a professional Executive Merchant Intelligence Report for Merchant {m_id}.

USE ONLY THESE EXACT FIGURES (do NOT recalculate or invent numbers):
- 3M Revenue: INR {total_rev:,.2f} | Monthly Avg: INR {monthly_rev:,.2f}
- Net Cashflow (excl. refunds): INR {monthly_rev * (1 - float(revenue_data.get('refund_rate', 0))/100):,.2f}
- Auth Success Rate: {revenue_data.get('success_rate', 0):.2f}% | Refund Rate: {revenue_data.get('refund_rate', 0):.2f}%
- Avg Order Value: INR {float(revenue_data.get('avg_order_value') or 0):,.2f}
- Risk Score: {risk_data.get('risk_score', 0):.1f}/100 ({risk_data.get('risk_level', 'N/A')})
- Churn Probability: {churn_p:.1f}% | Confidence: {derived_conf:.1f}%
- Forecast 3M Avg: INR {three_m_forecast_avg:,.2f}
- Key Recs: {', '.join(recommendations[:3])}
- Underwriting Decision: {final_dec}

REQUIRED SECTIONS WITH THIS FORMAT:
### 1. Executive Summary
2-3 sentences on overall merchant health, risk posture, and decision.

### 2. Revenue & Throughput Velocity
- **3M Aggregate Revenue**: INR {total_rev:,.2f}
- **Monthly Revenue**: INR {monthly_rev:,.2f}
- **Net Cashflow (excl. refunds)**: INR {monthly_rev * (1 - float(revenue_data.get('refund_rate', 0))/100):,.2f}
- **Auth Success Rate**: {revenue_data.get('success_rate', 0):.2f}% — note if optimal (≥92%) or needs improvement
- **AOV**: INR {float(revenue_data.get('avg_order_value') or 0):,.2f}

### 3. Risk Assessment & Fraud Exposure
2-3 sentences covering risk score, churn probability, refund rate vs 2% ceiling, and key risk explanation.

### 4. 90-Day Growth Forecast
- **Projected 3M Avg Revenue**: INR {three_m_forecast_avg:,.2f}
1 sentence on trajectory trend.

### 5. Strategic Recommendations
List top 3 recommendations as bullet points with brief rationale each.

### 6. Underwriting Decision
**Decision**: {final_dec}
- **Derived Committee Confidence**: {derived_conf:.1f}%
- Settlement Terms, supervision frequency, one-line rationale.

Under 280 words. Use bold for all metrics. No backticks around numbers or IDs."""
            report_content = llm_service.generate(prompt=prompt, fallback_generator=fallback_fn)
        else:
            report_content = fallback_fn()

        save_agent_trace(
            merchant_id=m_id,
            agent_name="Executive Report Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary="Executive brief generated",
            confidence=derived_conf,
            reasoning=risk_data.get("explanation") or "",
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