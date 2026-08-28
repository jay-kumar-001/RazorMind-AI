import { useState } from "react";
import { runSimulation } from "../api/api";
import { Sliders, RefreshCw, Zap, TrendingUp, CheckCircle, ArrowRight } from "lucide-react";

const cash = (v) =>
  `₹${Number(v || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

const SLIDERS = [
  { key: "success_rate_increase", label: "Authorization Rate Lift", unit: "%", min: 0, max: 15, step: 0.5, desc: "Smart routing & fallback retry" },
  { key: "refund_rate_reduction", label: "Refund / Dispute Reduction", unit: "%", min: 0, max: 8, step: 0.5, desc: "Pre-dispute alerts & rapid cancellation" },
  { key: "churn_rate_reduction", label: "Customer Churn Reduction", unit: "%", min: 0, max: 12, step: 0.5, desc: "Automated re-engagement sequences" },
  { key: "retention_increase", label: "Repeat Customer Lift", unit: "%", min: 0, max: 20, step: 0.5, desc: "Loyalty incentives & checkout speed" },
  { key: "volume_growth", label: "Organic Volume Expansion", unit: "%", min: 0, max: 40, step: 1.0, desc: "Marketing scale & ad spend increase" },
];

const PRESETS = {
  gateway: { name: "Gateway Optimization", values: { success_rate_increase: 4.0, refund_rate_reduction: 0.5, churn_rate_reduction: 1.0, retention_increase: 2.0, volume_growth: 5.0 } },
  dispute: { name: "Dispute Mitigation", values: { success_rate_increase: 1.0, refund_rate_reduction: 2.5, churn_rate_reduction: 3.0, retention_increase: 4.0, volume_growth: 0.0 } },
  growth: { name: "Aggressive Scale", values: { success_rate_increase: 3.0, refund_rate_reduction: 1.0, churn_rate_reduction: 2.0, retention_increase: 8.0, volume_growth: 20.0 } },
};

const defaultSliders = SLIDERS.reduce((acc, s) => ({ ...acc, [s.key]: 0 }), {});

export default function DigitalTwinTab({ merchant }) {
  const [sliders, setSliders] = useState(defaultSliders);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const mid = merchant?.merchant_id;

  const update = (key, value) => setSliders((s) => ({ ...s, [key]: Number(value) }));

  const applyPreset = (presetKey) => {
    const p = PRESETS[presetKey];
    if (p) setSliders(p.values);
  };

  const runSim = async () => {
    if (!mid) return;
    setLoading(true);
    setError("");
    try {
      const res = await runSimulation({ merchant_id: mid, ...sliders });
      setResult(res.data);
    } catch (e) {
      setError("Simulation model failed to converge. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setSliders(defaultSliders);
    setResult(null);
  };

  if (!merchant) {
    return (
      <div className="panel" style={{ textAlign: "center", padding: "40px 0" }}>
        <p style={{ color: "var(--text-tertiary)" }}>Load a merchant to run digital twin what-if simulations</p>
      </div>
    );
  }

  const baseRev = Number(merchant.total_revenue || 120000);
  const simRev = result?.simulated?.revenue || baseRev * (1 + (sliders.success_rate_increase + sliders.volume_growth) * 0.01);
  const revGrowth = result?.simulated?.revenue_growth_percent || ((simRev - baseRev) / baseRev) * 100;
  const netLift = simRev - baseRev;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="grid-split-1-2">
        {/* ── LEFT: SCENARIO PARAMETERS ───────────────────────────── */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">Digital Twin Parameter Controls</div>
              <div className="panel-title">What-If Hypothesis Deck</div>
            </div>
            <button className="btn btn-sm" onClick={reset}>
              <RefreshCw size={11} /> Reset
            </button>
          </div>

          {/* Quick Presets */}
          <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
            {Object.entries(PRESETS).map(([key, p]) => (
              <button
                key={key}
                className="btn btn-sm"
                style={{ fontSize: "11px", padding: "3px 8px" }}
                onClick={() => applyPreset(key)}
              >
                {p.name}
              </button>
            ))}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {SLIDERS.map((s) => (
              <div key={s.key} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px" }}>
                  <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>{s.label}</span>
                  <span style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--accent-text)" }}>
                    +{sliders[s.key]}{s.unit}
                  </span>
                </div>
                <input
                  type="range"
                  min={s.min}
                  max={s.max}
                  step={s.step}
                  value={sliders[s.key]}
                  onChange={(e) => update(s.key, e.target.value)}
                  style={{ accentColor: "var(--accent)", width: "100%", cursor: "pointer" }}
                />
                <span style={{ fontSize: "10.5px", color: "var(--text-tertiary)" }}>{s.desc}</span>
              </div>
            ))}
          </div>

          <button
            className="btn btn-primary"
            style={{ width: "100%", marginTop: 20, height: 36 }}
            onClick={runSim}
            disabled={loading}
          >
            {loading ? <><span className="spinner" /> Recalculating Digital Twin...</> : "Run Parameterized Simulation"}
          </button>
          {error && <p style={{ color: "var(--rose-text)", fontSize: "11.5px", marginTop: 8 }}>{error}</p>}
        </div>

        {/* ── RIGHT: SIMULATION LEDGER & OUTCOMES ──────────────────── */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">Simulated Outcome Ledger</div>
              <div className="panel-title">Projected Impact on Merchant Portfolio</div>
            </div>
            {result && <span className="tag tag-low">CONVERGED MODEL</span>}
          </div>

          {/* Top Big Impact Hero */}
          <div style={{
            background: "var(--bg-elevated)", border: "1px solid var(--border)",
            borderRadius: "var(--radius)", padding: "18px 20px", marginBottom: 16
          }}>
            <div style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-tertiary)", fontWeight: 600 }}>
              Net Projected Revenue Expansion
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 12, margin: "6px 0 2px" }}>
              <span style={{ fontSize: "30px", fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--emerald-text)" }}>
                +{Number(revGrowth).toFixed(2)}%
              </span>
              <span style={{ fontSize: "15px", color: "var(--text-primary)", fontWeight: 500, fontFamily: "var(--font-mono)" }}>
                (+{cash(netLift)} annual GMV lift)
              </span>
            </div>
            <div style={{ fontSize: "11.5px", color: "var(--text-secondary)" }}>
              Baseline: <strong style={{ color: "var(--text-primary)" }}>{cash(baseRev)}</strong> → Simulated Target: <strong style={{ color: "var(--emerald-text)" }}>{cash(simRev)}</strong>
            </div>
          </div>

          {/* Comparative Ledger Table */}
          <table className="data-table">
            <thead>
              <tr>
                <th>Operational Metric</th>
                <th>Baseline</th>
                <th>Simulated</th>
                <th>Projected Delta</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>Gross Annual Volume</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>{cash(baseRev)}</td>
                <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>{cash(simRev)}</td>
                <td style={{ fontFamily: "var(--font-mono)", color: "var(--emerald-text)", fontWeight: 600 }}>+{cash(netLift)}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>Payment Auth Rate</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>{Number(merchant.success_rate || 92).toFixed(1)}%</td>
                <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>
                  {(Number(merchant.success_rate || 92) + sliders.success_rate_increase).toFixed(1)}%
                </td>
                <td style={{ fontFamily: "var(--font-mono)", color: "var(--emerald-text)" }}>+{sliders.success_rate_increase.toFixed(1)}%</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>Refund / Return Velocity</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>{Number(merchant.refund_rate || 1.8).toFixed(2)}%</td>
                <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>
                  {Math.max(0.1, Number(merchant.refund_rate || 1.8) - sliders.refund_rate_reduction).toFixed(2)}%
                </td>
                <td style={{ fontFamily: "var(--font-mono)", color: "var(--emerald-text)" }}>-{sliders.refund_rate_reduction.toFixed(2)}%</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>Merchant Health Index</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>{Number(merchant.merchant_health_score || 74).toFixed(1)}</td>
                <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>
                  {Math.min(100, Number(merchant.merchant_health_score || 74) + sliders.success_rate_increase * 0.8 + sliders.refund_rate_reduction * 1.5).toFixed(1)}
                </td>
                <td style={{ fontFamily: "var(--font-mono)", color: "var(--emerald-text)" }}>
                  +{(sliders.success_rate_increase * 0.8 + sliders.refund_rate_reduction * 1.5).toFixed(1)} pts
                </td>
              </tr>
              <tr>
                <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>Underwriting Risk Score</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>{Number(merchant.risk_score || 28).toFixed(1)}</td>
                <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>
                  {Math.max(2.0, Number(merchant.risk_score || 28) - sliders.success_rate_increase * 1.2 - sliders.refund_rate_reduction * 2.0).toFixed(1)}
                </td>
                <td style={{ fontFamily: "var(--font-mono)", color: "var(--emerald-text)" }}>
                  -{(sliders.success_rate_increase * 1.2 + sliders.refund_rate_reduction * 2.0).toFixed(1)} pts
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
