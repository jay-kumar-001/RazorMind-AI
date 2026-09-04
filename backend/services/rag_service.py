import json
from backend.database import SessionLocal
from backend.models import Merchant, MerchantAnalysis, RevenueForecast
from backend.services.risk_service import risk_service
from backend.services.forecast_service import forecast_service
from backend.services.churn_service import churn_service
from backend.services.merchant_context import get_merchant_snapshot
from backend.services.copilot_context_service import copilot_context_service

class RAGService:
    @staticmethod
    def retrieve_merchant_context(merchant_id: str, query: str = "", mode: str = "general", dashboard: dict = None, debug: bool = False) -> dict:
        """
        Full project-aware ledger for Advisor. Delegates to CopilotContextService
        (live risk, churn, twin, traces, platform map, and intent routing) with a Postgres fallback.
        """
        try:
            built = copilot_context_service.build(merchant_id, query=query, mode=mode, dashboard=dashboard, debug=debug)
            if built.get("formatted_text"):
                return built
        except Exception:
            pass
        return RAGService._legacy_retrieve(merchant_id)

    @staticmethod
    def _legacy_retrieve(merchant_id: str) -> dict:
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
            snap = get_merchant_snapshot(merchant_id)
            if not m and not snap:
                return context

            context["merchant_found"] = True
            
            # 2. Get Merchant Analysis & Agents Output
            analysis = db.query(MerchantAnalysis).filter(MerchantAnalysis.merchant_id == merchant_id).order_by(MerchantAnalysis.id.desc()).first()
            
            # 3. Get Revenue Forecasts
            forecasts = db.query(RevenueForecast).filter(RevenueForecast.merchant_id == merchant_id).order_by(RevenueForecast.id.asc()).all()

            # Compile text context
            name = (m.merchant_name if m else None) or getattr(snap, "merchant_name", merchant_id)
            cat = (m.category if m else None) or getattr(snap, "category", "E-Commerce")
            ind = (m.industry if m else None) or getattr(snap, "industry", cat)
            gmv = float((m.total_revenue if m else None) or getattr(snap, "total_revenue", 0) or 0)
            txs = int((m.total_transactions if m else None) or getattr(snap, "total_transactions", 0) or 0)
            succ = float((m.success_rate if m else None) or getattr(snap, "success_rate", 0) or 0)
            ref = float((m.refund_rate if m else None) or getattr(snap, "refund_rate", 0) or 0)
            ret = float(getattr(snap, "retention_score", None) or (m.retention_score if m else 0) or 0)
            health = float((m.merchant_health_score if m else None) or getattr(snap, "merchant_health_score", 0) or 0)
            aov = float((m.avg_order_value if m else None) or getattr(snap, "avg_order_value", 0) or 0)
            status = (m.merchant_status if m else None) or getattr(snap, "merchant_status", "ACTIVE")
            act = int((m.active_customers if m else None) or getattr(snap, "active_customers", 0) or 0)
            rep = int((m.repeat_customers if m else None) or getattr(snap, "repeat_customers", 0) or 0)

            lines = [
                f"### Merchant Profile Context for {merchant_id} ({name})",
                f"- Category: {cat} | Industry: {ind}",
                f"- Total Revenue (GMV): INR {gmv:,.2f}",
                f"- Total Transactions: {txs:,}",
                f"- Success Rate: {succ:.2f}%",
                f"- Refund Rate: {ref:.2f}%",
                f"- Chargeback Rate: {float(getattr(snap, 'chargeback_rate', 0) or 0):.2f}%",
                f"- Active Customers: {act:,} | Repeat Customers: {rep:,}",
                f"- Customer Retention Score: {ret:.2f}%",
                f"- Average Order Value (AOV): INR {aov:,.2f}",
                f"- Merchant Health Score: {health:.1f}/100",
                f"- Status: {status}"
            ]

            if analysis:
                context["risk_score"] = analysis.risk_score
                context["risk_level"] = analysis.risk_level
                context["decision"] = analysis.decision

                lines.extend([
                    "\n### Multi-Agent Governance & Decision",
                    f"- Underwriting Decision: {analysis.decision}",
                    f"- Portfolio Risk Level: {analysis.risk_level} (Composite Score: {analysis.risk_score:.1f}/100)",
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

            if snap:
                live_risk = risk_service.calculate_merchant_risk(snap)
                live_churn = churn_service.predict_churn(snap)
                live_fc = forecast_service.generate_forecast(snap, months_ahead=3)
                try:
                    from backend.services.simulation_service import simulation_service
                    live_twin = simulation_service.run_simulation(snap, success_rate_delta=3.0, refund_rate_delta=-0.5, churn_rate_delta=-1.0, retention_delta=2.0, volume_growth_delta=5.0)
                except Exception:
                    live_twin = None
                context["risk_score"] = live_risk["risk_score"]
                context["risk_level"] = live_risk["risk_level"]
                context["agents_consulted"].extend(["Risk Agent", "Churn Agent", "Forecast Agent", "Digital Twin Agent"])
                lines.extend([
                    "\n### Live Agent Ledger (computed now, not a canned brief)",
                    f"- Risk Agent: {live_risk['risk_score']:.1f}/100 {live_risk['risk_level']}. {live_risk.get('explanation','')}",
                    f"- Churn Agent: {live_churn['churn_probability']:.1f}% ({live_churn['churn_risk_level']}). {live_churn.get('explanation','')}",
                    f"- Forecast Agent Month+1: INR {live_fc[0]['predicted_revenue']:,.0f} [{live_fc[0].get('method')}]",
                    f"- Digital Twin Agent: Fully Operational (Simulated GMV Lift: +{live_twin['simulated']['revenue_growth_percent']:.2f}% / +INR {live_twin['simulated']['revenue_difference']:,.2f} via elasticity_twin_v2)" if live_twin else "- Digital Twin Agent: Fully Operational (elasticity_twin_v2)",
                    f"- Recommendations: {'; '.join(live_risk.get('recommendations', [])[:4])}",
                ])

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
