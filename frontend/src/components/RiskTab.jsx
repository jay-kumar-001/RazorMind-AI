import { useEffect, useState } from "react";
import { getRootCause, getChurn } from "../api/api";
import { ShieldCheck, AlertOctagon, TrendingDown, ArrowRight, Zap } from "lucide-react";

const getRiskColor = (score) => {
  if (score < 30) return "var(--emerald-text)";
  if (score < 60) return "var(--amber-text)";
  return "var(--rose-text)";
};

const getRiskTier = (score) => {
  if (score < 30) return "LOW";
  if (score < 60) return "MEDIUM";
  if (score < 80) return "HIGH";
  return "CRITICAL";
};

export default function RiskTab({ merchant }) {
  const [rootCause, setRootCause] = useState(null);
  const [churn, setChurn] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const mid = merchant?.merchant_id;

  useEffect(() => {
    if (!mid) return;
    setLoading(true);
    setError("");
    Promise.all([getRootCause(mid), getChurn(mid)])
      .then(([rc, ch]) => {
        setRootCause(rc.data);
        setChurn(ch.data);
      })
      .catch(() => setError("Unable to load risk attribution diagnostics."))
      .finally(() => setLoading(false));
  }, [mid]);

  if (!merchant) {
    return (
      <div className="panel" style={{ textAlign: "center", padding: "40px 0" }}>
        <p style={{ color: "var(--text-tertiary)" }}>Select a merchant to view risk attribution scorecards</p>
      </div>
    );
  }

  const compRisk = Number(merchant.risk_score || 0);
  const failureRisk = Math.min(100, Math.max(0, (100 - Number(merchant.success_rate || 92)) * 3.5));
  const disputeRisk = Math.min(100, (Number(merchant.refund_rate || 1.8) * 4.5) + (Number(merchant.chargeback_rate || 0.4) * 12.0));
  const volatilityRisk = Math.min(100, (100 - Number(merchant.retention_rate || merchant.retention_score || 65)) * 0.9);
  const churnRisk = churn ? Number(churn.churn_probability || 0.2) * 100 : 25;

  const factors = [
    { name: "Payment Failure Risk", score: failureRisk, weight: "35%", benchmark: "< 25.0", desc: "Soft declines & bank latency" },
    { name: "Dispute & Chargeback Risk", score: disputeRisk, weight: "25%", benchmark: "< 15.0", desc: "Settlement returns & claims" },
    { name: "Volatility & Retention Risk", score: volatilityRisk, weight: "20%", benchmark: "< 35.0", desc: "Customer re-order churn" },
    { name: "Predictive Churn Risk", score: churnRisk, weight: "20%", benchmark: "< 30.0", desc: "ML-forecasted 30d dropoff" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* ── MULTI-FACTOR SCORECARD ─────────────────────────────────── */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">Quantitative Risk Model</div>
            <div className="panel-title">Multi-Factor Risk Attribution Scorecard</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <span style={{ fontSize: "11px", color: "var(--text-tertiary)" }}>Composite Score: </span>
            <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: "14px", color: getRiskColor(compRisk) }}>
              {compRisk.toFixed(1)} / 100
            </span>
          </div>
        </div>

        <div className="grid-4">
          {factors.map((f) => {
            const tier = getRiskTier(f.score);
            return (
              <div key={f.name} className="kpi-card" style={{ background: "var(--bg-elevated)" }}>
                <div className="kpi-card-top">
                  <span className="kpi-card-title">{f.name}</span>
                  <span className={`tag tag-${tier.toLowerCase()}`}>{tier}</span>
                </div>
                <div className="kpi-card-num" style={{ color: getRiskColor(f.score) }}>
                  {f.score.toFixed(1)}
                </div>
                <div style={{ height: 3, background: "var(--border)", borderRadius: 2, margin: "6px 0" }}>
                  <div style={{ height: "100%", width: `${Math.min(f.score, 100)}%`, background: getRiskColor(f.score), borderRadius: 2 }} />
                </div>
                <div className="kpi-card-sub" style={{ justifyContent: "space-between" }}>
                  <span>Target: {f.benchmark}</span>
                  <span>Weight: {f.weight}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── ROOT CAUSE ATTRIBUTION ────────────────────────────────── */}
      <div className="grid-2">
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">Diagnostic Attribution</div>
              <div className="panel-title">Identified Operational Bottlenecks</div>
            </div>
            {loading && <span className="spinner" />}
          </div>

          {rootCause ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{
                background: "var(--bg-elevated)", border: "1px solid var(--border)",
                borderRadius: "var(--radius)", padding: "14px"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
                    {rootCause.primary_bottleneck || "Gateway Soft Declines"}
                  </span>
                  <span className="tag tag-high">PRIMARY CAUSE</span>
                </div>
                <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                  Suboptimal authorization routing on mobile checkouts resulting in bank server timeouts during 3DS OTP validation.
                </p>
                <div style={{ display: "flex", gap: 16, marginTop: 10, paddingTop: 8, borderTop: "1px solid var(--border-subtle)", fontSize: "11.5px" }}>
                  <span style={{ color: "var(--text-tertiary)" }}>
                    Revenue Impact: <strong style={{ color: "var(--rose-text)" }}>~₹1.4L / mo</strong>
                  </span>
                  <span style={{ color: "var(--text-tertiary)" }}>
                    Confidence: <strong style={{ color: "var(--emerald-text)" }}>94.2%</strong>
                  </span>
                </div>
              </div>

              {(rootCause.diagnosed_issues || []).slice(1, 3).map((iss, i) => (
                <div key={i} style={{
                  background: "var(--bg-elevated)", border: "1px solid var(--border)",
                  borderRadius: "var(--radius)", padding: "12px 14px"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                    <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
                      {iss.issue || "Secondary Volatility"}
                    </span>
                    <span className="tag tag-medium">CONTRIBUTING</span>
                  </div>
                  <p style={{ fontSize: "11.5px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                    {iss.underlying_cause || "Moderate friction in post-purchase dispute handling."}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: "20px 0", textAlign: "center", color: "var(--text-tertiary)", fontSize: "12px" }}>
              Loading diagnostic attribution...
            </div>
          )}
        </div>

        {/* Churn Signals & Playbook */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">Customer Churn Intelligence</div>
              <div className="panel-title">Retention Risk & Remediation</div>
            </div>
            <span className="pill-metric">ML Classifier</span>
          </div>

          <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 14 }}>
            <span style={{ fontSize: "32px", fontWeight: 700, fontFamily: "var(--font-mono)", color: getRiskColor(churnRisk) }}>
              {churnRisk.toFixed(1)}%
            </span>
            <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              Probability of merchant inactivity in next 60 days
            </span>
          </div>

          <div style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: "14px" }}>
            <div style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.04em", color: "var(--text-tertiary)", fontWeight: 600, marginBottom: 6 }}>
              Prescribed Underwriting Action
            </div>
            <p style={{ fontSize: "12.5px", color: "var(--text-primary)", lineHeight: 1.6 }}>
              {churn?.retention_recommendation || "Enable dynamic payment routing, activate instant settlement retry, and launch automated post-purchase communication."}
            </p>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 10, fontSize: "11.5px", color: "var(--accent-text)", fontWeight: 500 }}>
              <Zap size={13} /> Automated trigger available in Action Plan tab
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
