import time
import logging
from typing import Dict, Any, List
from agents.revenue_agent import get_merchant_data
from backend.routes.traces import save_agent_trace
from backend.services.merchant_context import data_confidence

logger = logging.getLogger("razormind.agent.rootcause")


def rootcause_agent(merchant_id: str) -> Dict[str, Any]:
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")
        succ = float(getattr(merchant, "success_rate", 0.0) or 0.0)
        ref = float(getattr(merchant, "refund_rate", 0.0) or 0.0)
        cb = float(getattr(merchant, "chargeback_rate", 0.0) or 0.0)
        ret = float(getattr(merchant, "retention_score", 0.0) or 0.0)
        health = float(getattr(merchant, "merchant_health_score", 0.0) or 0.0)
        rev = float(getattr(merchant, "total_revenue", 0.0) or 0.0)

        diagnosed_issues: List[Dict[str, Any]] = []

        if succ < 90.0:
            loss = round(rev * ((94.0 - succ) / 100.0) * 0.9, 0)
            diagnosed_issues.append({
                "issue": "High Payment Gateway Decline Rate",
                "severity": "HIGH",
                "evidence": f"Success rate is {succ:.1f}% (benchmark >=94%)",
                "underlying_cause": "Soft declines and routing concentration on underperforming acquirers",
                "estimated_revenue_loss_pct": round((94.0 - succ) * 0.9, 1),
                "estimated_revenue_loss": loss,
            })
        elif succ < 93.0:
            loss = round(rev * ((94.0 - succ) / 100.0) * 0.7, 0)
            diagnosed_issues.append({
                "issue": "Moderate 3DS / OTP Dropoff",
                "severity": "MEDIUM",
                "evidence": f"Success rate is {succ:.1f}%",
                "underlying_cause": "Challenge friction on mobile checkout",
                "estimated_revenue_loss_pct": round((94.0 - succ) * 0.7, 1),
                "estimated_revenue_loss": loss,
            })

        if ref > 3.0:
            loss = round(rev * ((ref - 1.5) / 100.0), 0)
            diagnosed_issues.append({
                "issue": "Elevated Post-Purchase Refund & Dispute Rate",
                "severity": "HIGH",
                "evidence": f"Refund rate is {ref:.1f}% (ceiling 2.0%)",
                "underlying_cause": "Fulfillment, descriptor, or policy mismatch",
                "estimated_revenue_loss_pct": round((ref - 1.5) * 1.2, 1),
                "estimated_revenue_loss": loss,
            })
        elif ref > 2.0:
            loss = round(rev * ((ref - 1.5) / 100.0), 0)
            diagnosed_issues.append({
                "issue": "Moderate Refund Inflow",
                "severity": "MEDIUM",
                "evidence": f"Refund rate is {ref:.1f}%",
                "underlying_cause": "Occasional fulfillment mismatches",
                "estimated_revenue_loss_pct": round((ref - 1.5) * 0.8, 1),
                "estimated_revenue_loss": loss,
            })

        if cb > 1.0:
            diagnosed_issues.append({
                "issue": "Chargeback Rate Above Watch Threshold",
                "severity": "HIGH",
                "evidence": f"Chargeback rate {cb:.2f}% > 1.0%",
                "underlying_cause": "Weak representment and descriptor clarity",
                "estimated_revenue_loss_pct": round(cb * 1.1, 1),
                "estimated_revenue_loss": round(rev * (cb / 100.0), 0),
            })

        if ret < 20.0:
            diagnosed_issues.append({
                "issue": "Customer Churn & Weak Re-order Retention",
                "severity": "MEDIUM",
                "evidence": f"Repeat index {ret:.1f}% (target >=35%)",
                "underlying_cause": "Weak loyalty and post-purchase comms",
                "estimated_revenue_loss_pct": round((35.0 - ret) * 0.4, 1),
                "estimated_revenue_loss": round(rev * ((35.0 - ret) / 100.0) * 0.15, 0),
            })

        if not diagnosed_issues:
            diagnosed_issues.append({
                "issue": "Zero Critical Anomalies",
                "severity": "LOW",
                "evidence": f"KPIs in prime band (health {health:.1f})",
                "underlying_cause": "No material bottleneck vs underwriting policy",
                "estimated_revenue_loss_pct": 0.0,
                "estimated_revenue_loss": 0.0,
            })

        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        diagnosed_issues.sort(
            key=lambda x: (
                severity_order.get(str(x.get("severity", "LOW")).upper(), 3),
                -float(x.get("estimated_revenue_loss", 0.0) or 0.0),
            )
        )

        primary = diagnosed_issues[0]
        # Genuine diagnostic confidence derived from evidence strength, severity, and anomaly count
        issue_count = len([d for d in diagnosed_issues if d.get("severity") != "LOW"])
        severity_bonus = 12.0 if primary["severity"] == "HIGH" else (7.0 if primary["severity"] == "MEDIUM" else 2.0)
        conf = round(min(96.0, max(56.0, 70.0 + severity_bonus + min(8.0, issue_count * 3.0) + (4.0 if rev > 100000 else 0.0))), 1)

        reasoning = f"Primary bottleneck: {primary['issue']} — {primary['evidence']}"
        result = {
            "merchant_id": merchant_id,
            "primary_bottleneck": primary["issue"],
            "diagnosed_issues": diagnosed_issues,
            "total_issues_detected": issue_count,
            "confidence_score": conf,
            "reasoning_summary": reasoning,
            "estimated_monthly_loss": primary.get("estimated_revenue_loss", 0),
        }
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Root Cause Agent",
            execution_time=time.time() - start_time,
            status="SUCCESS",
            output_summary=reasoning,
            confidence=conf,
            reasoning=reasoning,
        )
        return result
    except Exception as e:
        logger.error("RootCause agent error for %s: %s", merchant_id, e)
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Root Cause Agent",
            execution_time=time.time() - start_time,
            status="FAILED",
            output_summary=str(e),
        )
        raise
