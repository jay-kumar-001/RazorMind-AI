import { useEffect, useState } from "react";
import { getTraces, getTracesSummary } from "../api/api";
import { Activity, Clock, CheckCircle, AlertCircle, RefreshCw, Cpu } from "lucide-react";

const PIPELINE_NODES = [
  { id: "revenue", label: "Revenue", desc: "Data extraction" },
  { id: "forecast", label: "Forecast", desc: "Exponential trends" },
  { id: "risk", label: "Risk Model", desc: "Multi-factor score" },
  { id: "churn", label: "Churn AI", desc: "Retention classifier" },
  { id: "rootcause", label: "Root Cause", desc: "Bottleneck attribution" },
  { id: "decision", label: "Decision", desc: "Underwriting policy" },
  { id: "action_plan", label: "Action Plan", desc: "Tactical roadmap" },
  { id: "executive_report", label: "Exec Brief", desc: "Boardroom memo" },
];

export default function ObservabilityTab({ merchant }) {
  const [traces, setTraces] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const mid = merchant?.merchant_id;

  const loadTelemetry = async () => {
    if (!mid) return;
    setLoading(true);
    setError("");
    try {
      const [tr, sum] = await Promise.all([getTraces(mid), getTracesSummary(mid)]);
      setTraces(Array.isArray(tr.data) ? tr.data : []);
      setSummary(sum.data);
    } catch {
      setError("Failed to fetch agent execution traces.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mid) loadTelemetry();
  }, [mid]);

  if (!merchant) {
    return (
      <div className="panel" style={{ textAlign: "center", padding: "40px 0" }}>
        <p style={{ color: "var(--text-tertiary)" }}>Select a merchant to inspect LangGraph execution telemetry</p>
      </div>
    );
  }

  const successCount = traces.filter((t) => (t.status || "SUCCESS").toUpperCase() === "SUCCESS").length;
  const avgLatency = traces.length
    ? (traces.reduce((sum, t) => sum + (t.execution_time_ms || t.duration_ms || 0), 0) / traces.length).toFixed(0)
    : "0";
  const successPct = traces.length ? ((successCount / traces.length) * 100).toFixed(0) : "0";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* ── TELEMETRY HERO METRIC STRIP ───────────────────────────── */}
      <div className="grid-4">
        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Total Agent Executions</span>
            <Cpu size={14} color="var(--text-tertiary)" />
          </div>
          <div className="kpi-card-num">{traces.length}</div>
          <div className="kpi-card-sub">Recorded spans for {mid}</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Success Rate</span>
            <CheckCircle size={14} color="var(--emerald-text)" />
          </div>
          <div className="kpi-card-num" style={{ color: "var(--emerald-text)" }}>
            {successPct}%
          </div>
          <div className="kpi-card-sub">{successCount} successful / {traces.length} spans</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">P50 Step Latency</span>
            <Clock size={14} color="var(--accent-text)" />
          </div>
          <div className="kpi-card-num" style={{ color: "var(--accent-text)" }}>
            {avgLatency}ms
          </div>
          <div className="kpi-card-sub">Average per-agent execution time</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-top">
            <span className="kpi-card-title">Active Orchestrator</span>
            <Activity size={14} color="var(--sky-text)" />
          </div>
          <div className="kpi-card-num" style={{ fontSize: "16px", color: "var(--sky-text)", marginTop: "12px" }}>
            LangGraph v0.2
          </div>
          <div className="kpi-card-sub">StateGraph DAG compiler</div>
        </div>
      </div>

      {/* ── LANGGRAPH PIPELINE DAG ─────────────────────────────────── */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">DAG Pipeline Topology</div>
            <div className="panel-title">LangGraph Agent Execution Sequence</div>
          </div>
          <button className="btn btn-sm" onClick={loadTelemetry} disabled={loading}>
            <RefreshCw size={11} /> Refresh Telemetry
          </button>
        </div>

        <div style={{
          display: "grid", gridTemplateColumns: `repeat(${PIPELINE_NODES.length}, 1fr)`,
          gap: 6, marginTop: 12, overflowX: "auto", paddingBottom: 6
        }}>
          {PIPELINE_NODES.map((node, i) => (
            <div
              key={node.id}
              style={{
                background: "var(--bg-elevated)", border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)", padding: "10px", minWidth: "100px"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-tertiary)" }}>
                  0{i + 1}
                </span>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--emerald)" }} />
              </div>
              <div style={{ fontSize: "11.5px", fontWeight: 600, color: "var(--text-primary)", whiteSpace: "nowrap" }}>
                {node.label}
              </div>
              <div style={{ fontSize: "9.5px", color: "var(--text-tertiary)", marginTop: 2, whiteSpace: "nowrap" }}>
                {node.desc}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── DATADOG STYLE SPAN EXECUTION LOG ───────────────────────── */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">Execution Traces</div>
            <div className="panel-title">Agent Telemetry Logs</div>
          </div>
          <span style={{ fontSize: "11px", color: "var(--text-tertiary)" }}>
            Showing latest spans
          </span>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: 40 }}>Status</th>
              <th>Agent</th>
              <th>Input / Reasoning</th>
              <th>Output</th>
              <th>Confidence</th>
              <th>Duration</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {traces.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ color: "var(--text-tertiary)", textAlign: "center", padding: 20 }}>
                  No traces yet for {mid}. Run the multi-agent pipeline from Executive Brief.
                </td>
              </tr>
            ) : traces.map((t, i) => (
              <tr key={t.id || i}>
                <td>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: (t.status || "").toUpperCase() === "FAILED" ? "var(--rose)" : "var(--emerald)", display: "inline-block" }} />
                </td>
                <td className="mono" style={{ fontWeight: 600 }}>
                  {t.agent_name || t.node_name || "Agent Node"}
                </td>
                <td style={{ color: "var(--text-secondary)", fontSize: "11.5px", maxWidth: 220 }}>
                  {t.reasoning || (typeof t.input === "string" ? t.input : JSON.stringify(t.source_metrics || {}).slice(0, 120))}
                </td>
                <td style={{ color: "var(--text-secondary)", fontSize: "12px" }}>
                  {t.output_summary || "—"}
                </td>
                <td className="mono">
                  {t.confidence != null ? `${Number(t.confidence).toFixed(1)}%` : "—"}
                </td>
                <td style={{ fontFamily: "var(--font-mono)", fontSize: "11.5px", color: "var(--text-primary)" }}>
                  {t.duration_ms || t.execution_time_ms || 0}ms
                </td>
                <td style={{ fontSize: "11px", color: "var(--text-tertiary)" }}>
                  {t.created_at ? new Date(t.created_at).toLocaleTimeString() : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
