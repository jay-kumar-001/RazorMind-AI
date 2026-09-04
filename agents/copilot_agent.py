import time
import logging
from typing import Optional
from agents.revenue_agent import get_merchant_data
from backend.database import SessionLocal
from backend.models import MerchantAnalysis
from backend.services.llm_service import llm_service
from backend.services.risk_service import risk_service
from backend.services.forecast_service import forecast_service
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.copilot")

def generate_copilot_fallback(merchant_info: dict, question: str) -> str:
    """
    High-fidelity deterministic fintech synthesis for Copilot when LLM is offline.
    """
    m_id = merchant_info.get("merchant_id", "Merchant")
    revenue = merchant_info.get("total_revenue", 0.0)
    success = merchant_info.get("success_rate", 0.0)
    refund = merchant_info.get("refund_rate", 0.0)
    health = merchant_info.get("merchant_health_score", 0.0)
    risk_level = merchant_info.get("risk_level", "LOW")
    decision = merchant_info.get("decision", "APPROVE")
    q_lower = question.lower()

    if any(k in q_lower for k in ["risk", "danger", "fraud", "safe", "threat", "failure"]):
        return (
            f"### Risk Intelligence for {m_id}\n\n"
            f"- **Current Risk Level**: **{risk_level}** (Health Score: {health:.1f}/100)\n"
            f"- **Authorization Success**: {success:.1f}% ({'Optimal' if success >= 92 else 'Underperforming — soft decline exposure'})\n"
            f"- **Refund & Dispute Velocity**: {refund:.1f}% ({'Healthy' if refund <= 2 else 'Elevated — potential chargeback drag'})\n"
            f"- **Risk Mitigation**: Recommend enabling dynamic retry policies and 3DS adaptive friction controls."
        )
    elif any(k in q_lower for k in ["revenue", "money", "growth", "forecast", "sales", "earnings"]):
        return (
            f"### Revenue & Growth Intelligence for {m_id}\n\n"
            f"- **Current Monthly Run-Rate**: INR {revenue:,.0f}\n"
            f"- **Projected Trajectory**: Expected 3-month momentum of +{((health - 50) * 0.05):.1f}% based on operational velocity.\n"
            f"- **Average Ticket Size**: INR {merchant_info.get('avg_order_value', 250):,.0f}\n"
            f"- **Growth Opportunity**: Improving payment authorization by +3% would yield approximately INR {(revenue * 0.035):,.0f}/month in captured revenue."
        )
    elif any(k in q_lower for k in ["recommend", "action", "improve", "do", "strategy", "roadmap"]):
        ret_display = float(merchant_info.get('retention_rate', merchant_info.get('retention_score', 48.6)) or 48.6)
        return (
            f"### Strategic Action Items for {m_id}\n\n"
            f"1. **Deploy Dynamic Payment Routing**: Minimize gateway timeouts and route to top-performing card acquirers.\n"
            f"2. **Chargeback Prevention Alerts**: Integrate real-time pre-dispute notifications to arrest rising refund rates.\n"
            f"3. **Customer Re-engagement**: Boost repeat customer retention ({ret_display:.1f}%) through tokenized checkout incentives."
        )
    elif any(k in q_lower for k in ["decision", "why", "status", "approve", "review"]):
        return (
            f"### Underwriting Decision Rationale for {m_id}\n\n"
            f"- **Final System Decision**: **{decision}**\n"
            f"- **Underwriting Score**: {health:.1f}/100\n"
            f"- **Core Justification**: Merchant exhibits {risk_level.lower()} risk fundamentals with a {success:.1f}% authorization rate and INR {revenue:,.0f} aggregate throughput.\n"
            f"- **Supervision Policy**: Maintain standard quarterly health audits and automated dispute alerts."
        )
    else:
        return (
            f"### Merchant Summary for {m_id}\n\n"
            f"- **Portfolio Status**: {merchant_info.get('merchant_status', 'Healthy')} | **Decision**: **{decision}**\n"
            f"- **Key Metrics**: Revenue: INR {revenue:,.0f} | Success Rate: {success:.1f}% | Refund Rate: {refund:.1f}%\n"
            f"- **Health Index**: {health:.1f}/100 ({risk_level} Risk)\n"
            f"- **Key Focus**: Focus on transaction retry optimization and customer retention."
        )

def copilot_agent(merchant_id: str, question: str) -> str:
    """
    Interactive Copilot agent answering questions using real-time merchant context.
    """
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            return f"Merchant {merchant_id} not found in the portfolio database."

        # Fetch latest analysis if available
        db = SessionLocal()
        latest_analysis = None
        try:
            latest_analysis = (
                db.query(MerchantAnalysis)
                .filter(MerchantAnalysis.merchant_id == merchant_id)
                .order_by(MerchantAnalysis.id.desc())
                .first()
            )
        finally:
            db.close()

        risk_data = risk_service.calculate_merchant_risk(merchant)
        forecast_data = forecast_service.generate_forecast(merchant, months_ahead=3)

        retention_val = float(getattr(merchant, "retention_rate", None) or getattr(merchant, "retention_score", 0.0) or 0.0)
        merchant_context = {
            "merchant_id": merchant_id,
            "merchant_name": getattr(merchant, "merchant_name", merchant_id),
            "category": getattr(merchant, "category", "E-Commerce"),
            "total_revenue": float(getattr(merchant, "total_revenue", 0.0) or 0.0),
            "success_rate": float(getattr(merchant, "success_rate", 0.0) or 0.0),
            "refund_rate": float(getattr(merchant, "refund_rate", 0.0) or 0.0),
            "retention_score": retention_val,
            "retention_rate": retention_val,
            "merchant_health_score": float(getattr(merchant, "merchant_health_score", 0.0) or 0.0),
            "risk_score": risk_data["risk_score"],
            "risk_level": risk_data["risk_level"],
            "merchant_status": getattr(merchant, "merchant_status", "Healthy"),
            "decision": latest_analysis.decision if latest_analysis else ("APPROVE" if risk_data["risk_score"] < 40 else "MONITOR CLOSELY"),
            "avg_order_value": float(getattr(merchant, "avg_order_value", 250.0) or 250.0),
            "forecast_next_month": forecast_data[0]["predicted_revenue"] if forecast_data else 0.0
        }

        prompt = f"""
You are the RazorMind AI Merchant Copilot, an elite fintech AI advisor for payments and merchant intelligence.

Merchant Profile Context:
- Merchant ID: {merchant_context['merchant_id']} ({merchant_context['merchant_name']})
- Industry / Category: {merchant_context['category']}
- Monthly Revenue: INR {merchant_context['total_revenue']:,.2f}
- Payment Success Rate: {merchant_context['success_rate']:.2f}%
- Refund Rate: {merchant_context['refund_rate']:.2f}%
- Customer Retention Rate: {merchant_context['retention_rate']:.1f}%
- Merchant Health Score: {merchant_context['merchant_health_score']:.2f}/100
- Risk Score: {merchant_context['risk_score']:.1f}/100 (Level: {merchant_context['risk_level']})
- Current Underwriting Decision: {merchant_context['decision']}
- Projected Next Month Revenue: INR {merchant_context['forecast_next_month']:,.2f}

User Question:
"{question}"

Instructions:
- Provide a clear, actionable, professional executive response in markdown paragraphs and lists.
- Ground your answer specifically in the provided merchant numbers.
- Do NOT wrap numbers, metrics, merchant IDs, risk scores, currency amounts, or percentages in markdown code backticks (e.g. write **45.2/100**, **M0001**, INR 10,25,351 instead of `45.2` or `M0001`). Use plain text or bold markdown.
- Never create single-value isolated code blocks.
- Highlight risk nuances, growth opportunities, and recommendations.
- Keep the tone comparable to Stripe Radar, Razorpay, or McKinsey Payments.
- Under 250 words.
"""
        fallback_fn = lambda: generate_copilot_fallback(merchant_context, question)
        answer = llm_service.generate(prompt=prompt, fallback_generator=fallback_fn)

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Copilot Agent",
            execution_time=exec_time,
            status="SUCCESS",
            input_query=question,
            output_summary=answer[:100] + "..."
        )
        return answer

    except Exception as e:
        logger.error(f"Copilot agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Copilot Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise