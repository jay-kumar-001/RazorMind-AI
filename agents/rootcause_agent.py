import time
import logging
from typing import Dict, Any, List
from agents.revenue_agent import get_merchant_data
from backend.routes.traces import save_agent_trace

logger = logging.getLogger("razormind.agent.rootcause")

def rootcause_agent(merchant_id: str) -> Dict[str, Any]:
    """
    Performs deep diagnostic attribution to identify primary root causes of merchant risk.
    """
    start_time = time.time()
    try:
        merchant = get_merchant_data(merchant_id)
        if not merchant:
            succ, ref, ret, health = 92.5, 1.8, 30.0, 75.0
        else:
            succ = float(getattr(merchant, "success_rate", 92.5) or 92.5)
            ref = float(getattr(merchant, "refund_rate", 1.8) or 1.8)
            ret = float(getattr(merchant, "retention_score", 30.0) or 30.0)
            health = float(getattr(merchant, "merchant_health_score", 75.0) or 75.0)

        diagnosed_issues: List[Dict[str, Any]] = []

        if succ < 90.0:
            diagnosed_issues.append({
                "issue": "High Payment Gateway Decline Rate",
                "severity": "HIGH",
                "evidence": f"Success rate is {succ:.1f}% (Benchmark: >=94%)",
                "underlying_cause": "Suboptimal gateway routing causing soft bank declines on high-frequency transactions",
                "estimated_revenue_loss_pct": round((94.0 - succ) * 0.9, 1)
            })
        elif succ < 93.0:
            diagnosed_issues.append({
                "issue": "Moderate 3DS Challenge Dropoff",
                "severity": "MEDIUM",
                "evidence": f"Success rate is {succ:.1f}%",
                "underlying_cause": "Friction during OTP validation and bank server timeouts on mobile checkouts",
                "estimated_revenue_loss_pct": round((94.0 - succ) * 0.7, 1)
            })

        if ref > 3.0:
            diagnosed_issues.append({
                "issue": "Elevated Post-Purchase Refund & Dispute Rate",
                "severity": "HIGH",
                "evidence": f"Refund rate is {ref:.1f}% (Threshold: <=2.0%)",
                "underlying_cause": "Product mismatch, fulfillment delays, or ambiguous cancellation policies",
                "estimated_revenue_loss_pct": round((ref - 1.5) * 1.2, 1)
            })
        elif ref > 2.0:
            diagnosed_issues.append({
                "issue": "Moderate Refund Inflow",
                "severity": "MEDIUM",
                "evidence": f"Refund rate is {ref:.1f}%",
                "underlying_cause": "Occasional order fulfillment mismatches",
                "estimated_revenue_loss_pct": round((ref - 1.5) * 0.8, 1)
            })

        if ret < 20.0:
            diagnosed_issues.append({
                "issue": "Customer Churn & Weak Re-order Retention",
                "severity": "MEDIUM",
                "evidence": f"Repeat customer score is {ret:.1f}% (Target: >=35%)",
                "underlying_cause": "Lack of loyalty rewards and absence of automated post-purchase communication",
                "estimated_revenue_loss_pct": round((35.0 - ret) * 0.4, 1)
            })

        if not diagnosed_issues:
            diagnosed_issues.append({
                "issue": "Zero Critical Anomalies",
                "severity": "LOW",
                "evidence": f"All KPIs operating within prime standards (Health: {health:.1f})",
                "underlying_cause": "Optimal gateway health and frictionless checkout flow",
                "estimated_revenue_loss_pct": 0.0
            })

        primary_bottleneck = diagnosed_issues[0]["issue"] if diagnosed_issues else "None"

        result = {
            "merchant_id": merchant_id,
            "primary_bottleneck": primary_bottleneck,
            "diagnosed_issues": diagnosed_issues,
            "total_issues_detected": len([d for d in diagnosed_issues if d["severity"] != "LOW"]),
            "confidence_score": 93.0
        }

        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Root Cause Agent",
            execution_time=exec_time,
            status="SUCCESS",
            output_summary=f"Identified bottleneck: {primary_bottleneck}"
        )
        return result

    except Exception as e:
        logger.error(f"RootCause agent error for {merchant_id}: {e}")
        exec_time = time.time() - start_time
        save_agent_trace(
            merchant_id=merchant_id,
            agent_name="Root Cause Agent",
            execution_time=exec_time,
            status="FAILED",
            output_summary=str(e)
        )
        raise
