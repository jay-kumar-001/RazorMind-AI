import os
import tempfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from agents.revenue_agent import revenue_agent
from agents.forecast_agent import forecast_agent
from agents.risk_agent import risk_agent
from agents.recommendation_agent import recommendation_agent
from agents.churn_agent import churn_agent
from agents.rootcause_agent import rootcause_agent
from agents.decision_agent import decision_agent

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

router = APIRouter(tags=["Reports"])

@router.get("/download-report/{merchant_id}")
def download_report(merchant_id: str):
    """
    Generates and downloads an investor-grade PDF merchant intelligence dossier.
    """
    try:
        rev = revenue_agent(merchant_id)
        fc = forecast_agent(merchant_id, months_ahead=3)
        risk = risk_agent(merchant_id)
        recs = recommendation_agent(merchant_id)
        churn = churn_agent(merchant_id)
        root = rootcause_agent(merchant_id)
        decision = decision_agent(risk, fc, merchant_id=merchant_id, churn=churn)

        temp_dir = tempfile.gettempdir()
        filename = f"{merchant_id}_intelligence_report.pdf"
        file_path = os.path.join(temp_dir, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1A1D2E"),
            alignment=0
        )
        h2_style = ParagraphStyle(
            'Heading2_Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#4F46E5"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body_Custom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#374151")
        )

        content = []

        # Title
        content.append(Paragraph("RazorMind AI — Merchant Intelligence Dossier", title_style))
        content.append(Paragraph(f"<b>Merchant Target</b>: {merchant_id} | <b>Category</b>: {rev.get('category', 'E-Commerce')} | <b>Status</b>: {rev.get('status', 'Healthy')}", body_style))
        content.append(Spacer(1, 14))

        # Metrics Table
        content.append(Paragraph("Core Financial & Processing Telemetry", h2_style))
        table_data = [
            ["Metric", "Value", "Benchmark", "Health Status"],
            ["Monthly Revenue", f"INR {rev.get('total_revenue', 0):,.0f}", "—", "Observed"],
            ["Success Rate", f"{rev.get('success_rate', 0):.2f}%", ">= 92.0%", "Optimal" if rev.get('success_rate', 0) >= 92 else "Action Needed"],
            ["Refund Rate", f"{rev.get('refund_rate', 0):.2f}%", "<= 2.0%", "Optimal" if rev.get('refund_rate', 0) <= 2 else "Elevated"],
            ["Composite Risk Score", f"{risk.get('risk_score', 0):.1f} / 100", "< 45.0", risk.get('risk_level', 'LOW')],
            ["Total Transactions", f"{rev.get('total_transactions', 0):,}", "500+", "Active"],
            ["Average Ticket (AOV)", f"INR {rev.get('avg_order_value', 0):,.0f}", "—", "Normal"]
        ]
        t = Table(table_data, colWidths=[150, 120, 110, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F9FAFB"), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        content.append(t)
        content.append(Spacer(1, 14))

        # Forecast Table
        content.append(Paragraph("3-Month Trend Forecast (95% Confidence Bounds)", h2_style))
        fc_table = [["Horizon", "Lower Bound (95%)", "Projected Revenue", "Upper Bound (95%)", "Expected Growth"]]
        for f in fc:
            fc_table.append([
                f.get("forecast_month", "Month"),
                f"INR {f.get('confidence_lower', 0):,.0f}",
                f"INR {f.get('predicted_revenue', 0):,.0f}",
                f"INR {f.get('confidence_upper', 0):,.0f}",
                f"+{f.get('growth_percent', 0):.1f}%"
            ])
        t_fc = Table(fc_table, colWidths=[100, 110, 120, 110, 80])
        t_fc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        content.append(t_fc)
        content.append(Spacer(1, 14))

        # Risk & Strategic Recommendations
        content.append(Paragraph("Prescribed Strategic Recommendations", h2_style))
        for r in recs[:5]:
            content.append(Paragraph(f"• {r}", body_style))

        content.append(Paragraph("Churn Analysis", h2_style))
        content.append(Paragraph(
            f"P(churn)={churn.get('churn_probability')}% ({churn.get('churn_risk_level')}). "
            f"{churn.get('explanation','')} Model: {churn.get('model')}.",
            body_style
        ))

        content.append(Paragraph("Root Cause", h2_style))
        content.append(Paragraph(
            f"Primary: {root.get('primary_bottleneck')}. Est. monthly leakage INR {root.get('estimated_monthly_loss', 0):,.0f}.",
            body_style
        ))
        for iss in (root.get("diagnosed_issues") or [])[:4]:
            content.append(Paragraph(
                f"• [{iss.get('severity')}] {iss.get('issue')} — {iss.get('evidence')}",
                body_style
            ))

        content.append(Paragraph("Underwriting Decision", h2_style))
        content.append(Paragraph(
            f"<b>{decision.get('final_decision')}</b> — {decision.get('decision_rationale')} "
            f"(confidence {decision.get('confidence_score')}%).",
            body_style
        ))

        content.append(Spacer(1, 14))
        content.append(Paragraph(
            f"<b>Data confidence</b>: {risk.get('confidence_score')}% (completeness + sample size, not a marketing 95%).",
            body_style
        ))

        doc.build(content)

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Generation failed: {str(e)}")