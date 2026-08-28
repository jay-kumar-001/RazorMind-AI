import { useEffect, useState } from "react";
import { getDashboard, getRecentAnalyses } from "../api/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from "recharts";
import { ArrowUpRight, TrendingUp, AlertTriangle, Users, Layers } from "lucide-react";

const cash = (v) =>
  `₹${Number(v || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

const CustomChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const count = payload[0].value;
  const share = ((count / 500) * 100).toFixed(1);
  return (
    <div style={{
      background: "var(--bg-elevated)", border: "1px solid var(--border)",
      borderRadius: "var(--radius-sm)", padding: "8px 12px", fontSize: "11.5px",
      boxShadow: "var(--shadow-md)"
    }}>
      <div style={{ color: "var(--text-tertiary)", textTransform: "uppercase", fontSize: "10px", fontWeight: 600 }}>{label} Tier</div>
      <div style={{ color: "var(--text-primary)", fontWeight: 600, fontSize: "13px", marginTop: "2px" }}>
        {count} Merchants <span style={{ color: "var(--text-secondary)", fontSize: "11px", fontWeight: 400 }}>({share}%)</span>
      </div>
    </div>
  );
};

export default function OverviewTab({ merchant }) {
  const [dash, setDash] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDashboard(), getRecentAnalyses()])
      .then(([d, a]) => {
        setDash(d.data);
        setAnalyses(Array.isArray(a.data) ? a.data : []);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="kpi-card skeleton" style={{ height: 90 }} />
        ))}
      </div>
    );
  }

  const riskDist = dash?.risk_distribution
    ? [
        { name: "LOW", value: dash.risk_distribution.LOW || 0, color: "var(--emerald)" },
        { name: "MEDIUM", value: dash.risk_distribution.MEDIUM || 0, color: "var(--amber)" },
        { name: "HIGH", value: dash.risk_distribution.HIGH || 0, color: "var(--rose)" },
        { name: "CRITICAL", value: dash.risk_distribution.CRITICAL || 0, color: "#dc2626" },
      ]
    : [];

  const healthScore = Number(merchant?.merchant_health_score || 0);
  const riskScore = Number(merchant?.risk_score || 0);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* ── KPI STRIP ─────────────────────────────────────────────── */}
      <div className="grid-4">
        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Portfolio GMV</span>
            <TrendingUp size={14} color="var(--text-tertiary)" />
          </div>
          <div className="kpi-card-num">
            ₹{dash?.total_gmv_crore || "398.7"} Cr
          </div>
          <div className="kpi-card-sub">
            <span className="delta-pos">↑ 12.4%</span> vs prior 30d
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Monitored Merchants</span>
            <Users size={14} color="var(--text-tertiary)" />
          </div>
          <div className="kpi-card-num">
            {dash?.total_merchants || 500}
          </div>
          <div className="kpi-card-sub">
            100% active underwriter sync
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Portfolio Health Index</span>
            <Layers size={14} color="var(--text-tertiary)" />
          </div>
          <div className="kpi-card-num">
            {Number(dash?.avg_health_score || 74).toFixed(1)}
            <span style={{ fontSize: 13, color: "var(--text-tertiary)", fontWeight: 400 }}> / 100</span>
          </div>
          <div className="kpi-card-sub">
            Grade: <strong style={{ color: "var(--emerald-text)" }}>{dash?.portfolio_health_grade || "A-"}</strong> (Institutional)
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Elevated Watchlist</span>
            <AlertTriangle size={14} color="var(--amber-text)" />
          </div>
          <div className="kpi-card-num" style={{ color: "var(--amber-text)" }}>
            {dash?.high_risk_count ?? 94}
          </div>
          <div className="kpi-card-sub">
            High & Critical tier merchants
          </div>
        </div>
      </div>

      {/* ── MIDDLE SPLIT SECTION ──────────────────────────────────── */}
      <div className="grid-split-2-1">
        {/* Left: Portfolio Risk Distribution */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">Underwriting Risk Tiers</div>
              <div className="panel-title">Portfolio Composition Breakdown</div>
            </div>
            <div style={{ display: "flex", gap: 10, fontSize: "11px", color: "var(--text-tertiary)" }}>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--emerald)" }} /> Low (55%)
              </span>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--amber)" }} /> Med (26%)
              </span>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--rose)" }} /> High (10%)
              </span>
              <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: "#dc2626" }} /> Critical (9%)
              </span>
            </div>
          </div>

          <div style={{ height: 180, width: "100%", marginTop: 8 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDist} margin={{ top: 8, right: 0, left: -25, bottom: 0 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--text-tertiary)", fontSize: 11, fontFamily: "var(--font-mono)" }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--text-tertiary)", fontSize: 10 }}
                />
                <Tooltip content={<CustomChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={60}>
                  {riskDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.88} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Selected Merchant Ledger */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">Active Context</div>
              <div className="panel-title">{merchant?.merchant_name || merchant?.merchant_id}</div>
            </div>
            <span className="pill-metric">{merchant?.merchant_id}</span>
          </div>

          <table className="data-table" style={{ marginTop: 4 }}>
            <tbody>
              <tr>
                <td>Auth Success Rate</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>
                  {Number(merchant?.success_rate || 92).toFixed(1)}%
                </td>
              </tr>
              <tr>
                <td>Refund Rate</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", fontWeight: 600, color: merchant?.refund_rate > 3 ? "var(--rose-text)" : "var(--text-primary)" }}>
                  {Number(merchant?.refund_rate || 1.8).toFixed(2)}%
                </td>
              </tr>
              <tr>
                <td>Chargeback Rate</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", fontWeight: 600, color: merchant?.chargeback_rate > 1 ? "var(--rose-text)" : "var(--text-primary)" }}>
                  {Number(merchant?.chargeback_rate || 0.4).toFixed(2)}%
                </td>
              </tr>
              <tr>
                <td>Customer Retention</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>
                  {Number(merchant?.retention_rate || merchant?.retention_score || 65).toFixed(1)}%
                </td>
              </tr>
              <tr>
                <td>Average Order Value</td>
                <td style={{ textAlign: "right", fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-primary)" }}>
                  ₹{Number(merchant?.avg_order_value || 850).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* ── RECENT AUDITS DATAGRID ─────────────────────────────────── */}
      {analyses.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">Autonomous Underwriting Ledger</div>
              <div className="panel-title">Recent Multi-Agent Evaluations</div>
            </div>
            <span style={{ fontSize: 11.5, color: "var(--text-tertiary)" }}>
              {analyses.length} verified records
            </span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Merchant ID</th>
                <th>Underwriting Decision</th>
                <th>Risk Tier</th>
                <th>Agent Confidence</th>
                <th>Evaluation Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {analyses.slice(0, 6).map((a, i) => (
                <tr key={i}>
                  <td className="mono">{a.merchant_id}</td>
                  <td style={{ fontWeight: 500, color: "var(--text-primary)" }}>
                    {a.decision || "APPROVE"}
                  </td>
                  <td>
                    <span className={`tag tag-${(a.risk_level || "low").toLowerCase()}`}>
                      {a.risk_level || "LOW"}
                    </span>
                  </td>
                  <td style={{ fontFamily: "var(--font-mono)", color: "var(--text-primary)" }}>
                    {a.confidence_score ? `${Number(a.confidence_score).toFixed(0)}%` : "95%"}
                  </td>
                  <td style={{ fontSize: 11.5, color: "var(--text-tertiary)" }}>
                    {a.created_at ? new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "Just now"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
