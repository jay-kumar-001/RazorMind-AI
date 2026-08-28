import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { getActionPlan } from "../api/api";
import { CheckCircle2, Calendar, TrendingUp, ShieldCheck, PlayCircle } from "lucide-react";

const cash = (v) =>
  `₹${Number(v || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

export default function ActionPlanTab({ merchant }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const mid = merchant?.merchant_id;

  const loadPlan = async () => {
    if (!mid) return;
    setLoading(true);
    setError("");
    try {
      const res = await getActionPlan(mid);
      setPlan(res.data);
    } catch {
      setError("Failed to load 30-day action roadmap.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mid) loadPlan();
  }, [mid]);

  if (!merchant) {
    return (
      <div className="panel" style={{ textAlign: "center", padding: "40px 0" }}>
        <p style={{ color: "var(--text-tertiary)" }}>Select a merchant to generate a 30-day tactical roadmap</p>
      </div>
    );
  }

  const milestones = [
    { week: "Week 1", title: "Settlement Triage & Hard Controls", owner: "Risk Underwriter", status: "READY", items: ["Audit 3DS OTP dropoff logs", "Enable dynamic retry for soft bank declines", "Verify settlement velocity"] },
    { week: "Week 2", title: "Payment Routing & Gateway Optimization", owner: "Payment Eng", status: "SCHEDULED", items: ["Implement multi-gateway load balancing", "Activate pre-dispute early alerts", "Tune fraud detection sensitivity"] },
    { week: "Week 3", title: "Customer Retention & Churn Safeguards", owner: "Merchant Success", status: "SCHEDULED", items: ["Deploy automated re-engagement sequence", "Enable tokenized checkout retry", "Configure VIP tier incentives"] },
    { week: "Week 4", title: "Executive Audit & Underwriting Signoff", owner: "Credit Committee", status: "PLANNED", items: ["Review 30d KPI stabilization metrics", "Confirm risk tier reclassification", "Authorize revised GMV threshold"] },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* ── ROADMAP SUMMARY STRIP ─────────────────────────────────── */}
      <div className="grid-3">
        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Roadmap Scope</span>
            <Calendar size={14} color="var(--text-tertiary)" />
          </div>
          <div className="kpi-card-num">30 Days</div>
          <div className="kpi-card-sub">4 sequential milestones</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Target GMV Recapture</span>
            <TrendingUp size={14} color="var(--emerald-text)" />
          </div>
          <div className="kpi-card-num" style={{ color: "var(--emerald-text)" }}>
            {plan?.expected_revenue_impact ? cash(plan.expected_revenue_impact) : "₹1,45,000"}
          </div>
          <div className="kpi-card-sub">Estimated 30d recovered revenue</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Target Risk Tier</span>
            <ShieldCheck size={14} color="var(--sky-text)" />
          </div>
          <div className="kpi-card-num" style={{ color: "var(--sky-text)" }}>
            LOW RISK
          </div>
          <div className="kpi-card-sub">Post-remediation classification</div>
        </div>
      </div>

      {/* ── CONSULTING TIMELINE VIEW ───────────────────────────────── */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">Tactical Milestone Execution</div>
            <div className="panel-title">Four-Week Operational Remediation Schedule</div>
          </div>
          <button className="btn btn-sm" onClick={loadPlan} disabled={loading}>
            {loading ? <span className="spinner" /> : "Regenerate Plan"}
          </button>
        </div>

        <div className="grid-4" style={{ marginTop: 8 }}>
          {milestones.map((m, i) => (
            <div key={m.week} style={{
              background: "var(--bg-elevated)", border: "1px solid var(--border)",
              borderRadius: "var(--radius)", padding: "16px", display: "flex", flexDirection: "column", justifyContent: "space-between"
            }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", fontWeight: 600, color: "var(--accent-text)" }}>
                    {m.week}
                  </span>
                  <span className="tag tag-neutral" style={{ fontSize: "10px" }}>{m.status}</span>
                </div>
                <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", marginBottom: 12, lineHeight: 1.4 }}>
                  {m.title}
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {m.items.map((item, j) => (
                    <div key={j} style={{ display: "flex", alignItems: "flex-start", gap: 6, fontSize: "11.5px", color: "var(--text-secondary)" }}>
                      <CheckCircle2 size={12} color="var(--emerald-text)" style={{ flexShrink: 0, marginTop: 2 }} />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ marginTop: 14, paddingTop: 8, borderTop: "1px solid var(--border-subtle)", fontSize: "10.5px", color: "var(--text-tertiary)" }}>
                Owner: <strong style={{ color: "var(--text-secondary)" }}>{m.owner}</strong>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── DETAILED DIRECTIVE REPORT ──────────────────────────────── */}
      {plan?.action_plan && (
        <div className="panel" style={{ lineHeight: 1.7 }}>
          <div className="eyebrow" style={{ marginBottom: 12 }}>Consulting Directive</div>
          <ReactMarkdown
            components={{
              h3: ({ children }) => (
                <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: "16px 0 8px" }}>
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p style={{ color: "var(--text-secondary)", fontSize: "12.5px", marginBottom: "8px" }}>{children}</p>
              ),
              li: ({ children }) => (
                <li style={{ color: "var(--text-secondary)", fontSize: "12.5px", marginBottom: "4px", marginLeft: "16px" }}>
                  {children}
                </li>
              ),
              strong: ({ children }) => <strong style={{ color: "var(--text-primary)" }}>{children}</strong>,
            }}
          >
            {plan.action_plan}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}
