import json
from backend.database import SessionLocal
from backend.models import Merchant, MerchantAnalysis, RevenueForecast

class RAGService:
    @staticmethod
    def retrieve_merchant_context(merchant_id: str) -> dict:
        """
        Retrieves the complete risk ledger, monthly forecasts, multi-agent decisions, 
        and action plans for a merchant from PostgreSQL databases to construct the RAG context.
        """
        db = SessionLocal()
        context = {
            "merchant_found": False,
            "formatted_text": "",
            "risk_score": 0.0,
            "risk_level": "LOW",
            "decision": "APPROVE",
            "agents_consulted": ["Revenue Agent", "KPI & Benchmark Agent"]
        }

        try:
            # 1. Get Merchant General KPIs
            m = db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()
            if not m:
                return context

            context["merchant_found"] = True
            
            # 2. Get Merchant Analysis & Agents Output
            analysis = db.query(MerchantAnalysis).filter(MerchantAnalysis.merchant_id == merchant_id).order_by(MerchantAnalysis.id.desc()).first()
            
            # 3. Get Revenue Forecasts
            forecasts = db.query(RevenueForecast).filter(RevenueForecast.merchant_id == merchant_id).order_by(RevenueForecast.id.asc()).all()

            # Compile text context
            lines = [
                f"### Merchant Profile Context for {merchant_id} ({m.merchant_name or 'Unknown'})",
                f"- Category: {m.category or 'E-Commerce'} | Industry: {m.industry or 'Retail'}",
                f"- Total Revenue (GMV): INR {m.total_revenue:,.2f}",
                f"- Total Transactions: {m.total_transactions:,}",
                f"- Success Rate: {m.success_rate:.2f}%",
                f"- Refund Rate: {m.refund_rate:.2f}%",
                f"- Active Customers: {m.active_customers:,} | Repeat Customers: {m.repeat_customers:,}",
                f"- Customer Retention Score: {m.retention_score:.2f}%",
                f"- Average Order Value (AOV): INR {m.avg_order_value:,.2f}",
                f"- Merchant Health Score: {m.merchant_health_score:.1f}/100",
                f"- Status: {m.merchant_status or 'Active'}"
            ]

            if analysis:
                context["risk_score"] = analysis.risk_score
                context["risk_level"] = analysis.risk_level
                context["decision"] = analysis.decision

                lines.extend([
                    "\n### Multi-Agent Governance & Decision",
                    f"- Underwriting Decision: `{analysis.decision}`",
                    f"- Portfolio Risk Level: `{analysis.risk_level}` (Composite Score: {analysis.risk_score:.1f}/100)",
                    f"- Executive Brief Report:\n{analysis.executive_report}",
                ])

                if analysis.root_causes:
                    try:
                        rc_data = json.loads(analysis.root_causes)
                        context["agents_consulted"].append("Root Cause Agent")
                        if isinstance(rc_data, dict):
                            lines.extend([
                                "\n### Identified Operational Bottlenecks (Root Cause Agent)",
                                f"- Primary Bottleneck: {rc_data.get('primary_bottleneck', 'None')}",
                                f"- Severity: {rc_data.get('severity', 'LOW')}",
                                f"- Diagnostic Evidence: {rc_data.get('evidence', 'No specific gateway anomaly detected')}"
                            ])
                    except Exception:
                        lines.extend([
                            "\n### Root Cause Evidence",
                            analysis.root_causes
                        ])

                if analysis.action_plan:
                    context["agents_consulted"].extend(["Risk Agent", "Action Plan Agent"])
                    lines.extend([
                        "\n### 30-Day Tactical Playbook (Action Plan Agent)",
                        analysis.action_plan
                    ])
                
                if analysis.recommendations:
                    context["agents_consulted"].append("Recommendation Agent")
                    try:
                        recs = json.loads(analysis.recommendations)
                        if isinstance(recs, list):
                            lines.extend(["\n### Core Recommendations:", *[f"- {r}" for r in recs]])
                        else:
                            lines.extend(["\n### Recommendations:", str(recs)])
                    except Exception:
                        lines.extend(["\n### Recommendations:", analysis.recommendations])

            if forecasts:
                context["agents_consulted"].append("Forecast Agent")
                lines.append("\n### Revenue Projections & Volatility (Forecast Agent)")
                for f in forecasts:
                    lines.append(
                        f"- Horizon '{f.forecast_month}': Expected Revenue: INR {f.predicted_revenue:,.2f} "
                        f"(Bounds: INR {f.confidence_lower:,.2f} - INR {f.confidence_upper:,.2f}) | Trend: {f.trend_slope or 0.0}%"
                    )

            context["formatted_text"] = "\n".join(lines)
            
            # Staggered unique agents consulted list
            context["agents_consulted"] = list(set(context["agents_consulted"]))

        except Exception as e:
            # Safe rollback
            db.rollback()
            context["formatted_text"] = f"[RAG Retrieval Error: Could not query postgres analysis logs. ({str(e)})]"
        finally:
            db.close()

        return context

rag_service = RAGService()
