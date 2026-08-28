import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getExecutiveReport, getDecision, getPdfUrl, triggerAnalysis } from "../api/api";
import { Download, PlayCircle, RefreshCw, CheckCircle, AlertTriangle, XCircle, Sparkles } from "lucide-react";

const cash = (v) =>
  `₹${Number(v || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

const DecisionCallout = ({ decision, rationale }) => {
  if (!decision) return null;
  const d = decision.toUpperCase();
  const isApproved = d.includes("APPROVE") && !d.includes("MONITOR");
  const isMonitor = d.includes("MONITOR") || d.includes("WATCH") || d.includes("CLOSELY");
  
  const bg = isApproved ? "var(--emerald-subtle)" : isMonitor ? "var(--amber-subtle)" : "var(--rose-subtle)";
  const border = isApproved ? "var(--emerald-border)" : isMonitor ? "var(--amber-border)" : "var(--rose-border)";
  const color = isApproved ? "var(--emerald-text)" : isMonitor ? "var(--amber-text)" : "var(--rose-text)";
  const Icon = isApproved ? CheckCircle : isMonitor ? AlertTriangle : XCircle;

  return (
    <div style={{
      background: bg, border: `1px solid ${border}`,
      borderRadius: "var(--radius)", padding: "14px 18px", marginBottom: 20
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, color, fontWeight: 700, fontSize: "13.5px", letterSpacing: "0.01em" }}>
        <Icon size={16} />
        UNDERWRITING DETERMINATION: {decision}
      </div>
      {rationale && (
        <p style={{ color: "var(--text-secondary)", fontSize: "12px", marginTop: "6px", lineHeight: 1.5 }}>
          {rationale}
        </p>
      )}
    </div>
  );
};

export default function ExecutiveTab({ merchant }) {
  const [report, setReport] = useState(null);
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const mid = merchant?.merchant_id;

  const loadData = async () => {
    if (!mid) return;
    setLoading(true);
    setError("");
    try {
      const [rep, dec] = await Promise.all([getExecutiveReport(mid), getDecision(mid)]);
      if (rep.data) setReport(rep.data);
      if (dec.data) setDecision(dec.data);
    } catch {
      setError("Unable to load executive briefing dossier.");
    } finally {
      setLoading(false);
    }
  };

  const reRunAnalysis = async () => {
    if (!mid) return;
    setAnalyzing(true);
    try {
      await triggerAnalysis(mid);
      await loadData();
    } catch {
      setError("Pipeline execution failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    if (mid) loadData();
  }, [mid]);

  if (!merchant) {
    return (
      <div className="panel" style={{ textAlign: "center", padding: "40px 0" }}>
        <p style={{ color: "var(--text-tertiary)" }}>Select a merchant to view executive underwriting brief</p>
      </div>
    );
  }

  const defaultContent = `### 1. Executive Summary
Merchant **${merchant.merchant_name || mid}** (${mid}) operates in the **${merchant.category || "E-Commerce"}** sector with annualized gross volume of **${cash(merchant.total_revenue || 1025350)}**. The business exhibits a **${merchant.risk_level || "MEDIUM"}** operational risk posture with an aggregate underwriting health index of **${Number(merchant.merchant_health_score || 64.8).toFixed(1)}/100**.

### 2. Revenue Insights & Throughput Velocity
- **Gross Processing Run-Rate**: ${cash(merchant.total_revenue || 1025350)} / year
- **Authorization Success Rate**: ${Number(merchant.success_rate || 93.5).toFixed(2)}% (Optimal processing baseline)
- **Refund & Chargeback Velocity**: ${Number(merchant.refund_rate || 4.1).toFixed(2)}% (Underwriting threshold: <= 5.0%)
- **Average Ticket Value (AOV)**: ₹${Number(merchant.avg_order_value || 393).toFixed(0)}

### 3. Risk Assessment & Fraud Signal Exposure
- **Composite Risk Score**: ${Number(merchant.risk_score || 45.2).toFixed(1)} / 100 (Tier: ${merchant.risk_level || "MEDIUM"})
- **Diagnostic Finding**: Payment flow demonstrates stable transaction velocity with moderate post-purchase refund inquiries.
- **Fraud Signal Exposure**: Zero critical anomaly alerts detected across primary card network telemetry.

### 4. Growth Outlook & 90-Day Forecast Trajectory
- **Projected 3-Month Run Rate**: ${cash((merchant.total_revenue || 1025350) / 12 * 1.08)} / month
- **Quarterly Momentum**: +6.8% expansion anticipated based on exponential smoothing model.
- **Statistical Confidence**: 95% confidence variance constrained within acceptable institutional thresholds.

### 5. Strategic Recommendations & Action Playbook
1. Audit merchant fulfillment latency and return policy communication to lower dispute volume.
2. Implement pre-chargeback dispute alert integrations (Ethoca / Verifi) for early resolution.
3. Configure dynamic gateway retry rules for mobile checkout OTP timeouts.

### 6. Final Underwriting Decision
- **Decision**: ${decision?.final_decision || "APPROVE WITH MONITORING"}
- **Settlement Terms**: T+1 Standard Settlement with automated dispute reserves.
- **Audit Confidence**: ${Number(decision?.confidence_score || report?.confidence_score || 95).toFixed(0)}%`;

  const reportText = report?.report || "No executive report is available yet. Re-run the multi-agent pipeline to generate a data-grounded briefing.";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* ── ACTION BAR ────────────────────────────────────────────── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className="tag tag-neutral">CONFIDENTIAL</span>
          <span style={{ fontSize: "12px", color: "var(--text-tertiary)" }}>
            Institutional Credit & Risk Underwriting Dossier
          </span>
          {loading && (
            <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: "11px", color: "var(--accent-text)", marginLeft: 8 }}>
              <span className="spinner" /> Synthesizing AI Brief...
            </span>
          )}
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-sm" onClick={loadData} disabled={loading}>
            <RefreshCw size={12} /> Refresh
          </button>
          <a
            href={getPdfUrl(mid)}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-emerald btn-sm"
          >
            <Download size={12} /> Export PDF Dossier
          </a>
          <button className="btn btn-primary btn-sm" onClick={reRunAnalysis} disabled={analyzing}>
            {analyzing ? <><span className="spinner" /> Synthesizing...</> : <><PlayCircle size={12} /> Re-run Multi-Agent Pipeline</>}
          </button>
        </div>
      </div>

      {error && <p style={{ color: "var(--rose-text)", fontSize: "12px" }}>{error}</p>}

      {/* ── BOARDROOM MEMORANDUM DOCUMENT ─────────────────────────── */}
      <div className="briefing-memo">
        <div className="briefing-header">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <div style={{ fontSize: "17px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>
              Merchant Credit & Operational Risk Memorandum
            </div>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-tertiary)" }}>
              REF: {mid}-{new Date().getFullYear()}
            </span>
          </div>

          <div className="briefing-meta-grid">
            <div>
              <div className="eyebrow">Subject Entity</div>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
                {merchant.merchant_name || mid}
              </div>
            </div>
            <div>
              <div className="eyebrow">Underwriter</div>
              <div style={{ fontSize: "13px", fontWeight: 500, color: "var(--text-primary)" }}>
                Autonomous AI Agent Committee
              </div>
            </div>
            <div>
              <div className="eyebrow">Audit Confidence</div>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--emerald-text)", fontFamily: "var(--font-mono)" }}>
                {decision?.confidence_score ?? report?.confidence_score ?? "—"}{(decision?.confidence_score ?? report?.confidence_score) != null ? "%" : ""}
              </div>
            </div>
            <div>
              <div className="eyebrow">Date Generated</div>
              <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
              </div>
            </div>
          </div>
        </div>

        {/* Determination Banner */}
        <DecisionCallout
          decision={decision?.final_decision}
          rationale={decision?.decision_rationale}
        />

        {/* Structured Executive Brief Markdown */}
        <div className="briefing-body">
          <ReactMarkdown
            components={{
              h2: ({ children }) => <h2>{children}</h2>,
              h3: ({ children }) => (
                <h3 style={{ fontSize: "13.5px", fontWeight: 600, color: "var(--accent-text)", margin: "16px 0 6px" }}>
                  {children}
                </h3>
              ),
              h4: ({ children }) => (
                <h4 style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", margin: "14px 0 4px" }}>
                  {children}
                </h4>
              ),
              p: ({ children }) => <p>{children}</p>,
              li: ({ children }) => <li style={{ marginLeft: "18px", marginBottom: "4px" }}>{children}</li>,
              strong: ({ children }) => <strong style={{ color: "var(--text-primary)" }}>{children}</strong>,
              code: ({ children }) => (
                <code style={{ background: "var(--bg-subtle)", padding: "2px 5px", borderRadius: "3px", fontFamily: "var(--font-mono)", fontSize: "11.5px" }}>
                  {children}
                </code>
              ),
            }}
          >
            {reportText}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
