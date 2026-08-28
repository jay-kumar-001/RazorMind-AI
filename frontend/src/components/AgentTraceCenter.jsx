import { motion } from "framer-motion";
import { Activity, CheckCircle2, Clock3 } from "lucide-react";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const agentNames = [
  "Revenue Agent",
  "Forecast Agent",
  "Risk Agent",
  "Recommendation Agent",
  "Decision Agent"
];

const shortName = (name) => String(name || "").replace(/\s+agent$/i, "");
const isSuccess = (status) => ["success", "completed", "complete"].includes(String(status || "").toLowerCase());
const dateTime = (value) => (value ? new Date(value).toLocaleString() : "—");
const duration = (value) => `${Number(value || 0).toFixed(Number(value) % 1 ? 1 : 0)} ms`;

export default function AgentTraceCenter({ traces, loading, error }) {
  const latest = [...traces]
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
    .slice(0, 10);

  const summaries = agentNames.map((name) => {
    const matches = traces.filter((trace) => String(trace.agent_name || "").toLowerCase() === name.toLowerCase());
    const average = matches.length ? matches.reduce((total, trace) => total + Number(trace.execution_time || 0), 0) / matches.length : 0;
    const newest = [...matches].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))[0];
    return { name, runs: matches.length, average, latest: newest, status: newest?.status || "No data" };
  });

  const totalRuns = traces.length;
  const successfulRuns = traces.filter((trace) => isSuccess(trace.status)).length;
  const successRate = totalRuns ? Math.round((successfulRuns / totalRuns) * 100) : 0;
  const overallAverage = totalRuns ? traces.reduce((total, trace) => total + Number(trace.execution_time || 0), 0) / totalRuns : 0;
  const executionData = summaries.map((summary) => ({ name: shortName(summary.name), time: Number(summary.average.toFixed(1)) }));
  const successData = [{ name: "Success", value: successfulRuns }, { name: "Other", value: Math.max(totalRuns - successfulRuns, 0) }];

  return (
    <section className="panel full-panel trace-center">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">OBSERVABILITY</p>
          <h2>Agent intelligence center</h2>
        </div>
        <span className="trace-live"><Activity size={14} /> Live execution telemetry</span>
      </div>
      {loading && <p className="section-status">Loading agent insights...</p>}
      {error && <p className="section-error">{error}</p>}
      {!loading && !error && <>
        <div className="agent-overview-grid">
          {summaries.map((summary, index) => <motion.article className="agent-overview-card" key={summary.name} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.06 }} whileHover={{ y: -3 }}>
            <span className={`status-orb ${isSuccess(summary.status) ? "healthy" : "neutral"}`} />
            <h3>{shortName(summary.name)}</h3>
            <p>Avg. execution <b>{duration(summary.average)}</b></p>
            <div><span>{summary.runs} total runs</span><strong>{summary.status}</strong></div>
          </motion.article>)}
        </div>

        <div className="workflow-and-analytics">
          <article className="workflow-card">
            <p className="eyebrow">LANGGRAPH WORKFLOW</p>
            <h3>Decision pipeline</h3>
            <div className="workflow-flow">
              {agentNames.map((name, index) => <div className="workflow-node-wrap" key={name}>
                <motion.div className="workflow-node" animate={{ boxShadow: ["0 0 0 rgba(169,157,255,0)", "0 0 20px rgba(169,157,255,.32)", "0 0 0 rgba(169,157,255,0)"] }} transition={{ duration: 2.2, delay: index * 0.2, repeat: Infinity }}><CheckCircle2 size={15} />{shortName(name)}</motion.div>
                {index < agentNames.length - 1 && <motion.span className="workflow-connector" initial={{ scaleY: 0 }} animate={{ scaleY: 1 }} transition={{ duration: 0.45, delay: index * 0.15 }} />}
              </div>)}
            </div>
          </article>
          <article className="analytics-card">
            <p className="eyebrow">AGENT ANALYTICS</p>
            <div className="analytics-stats"><div><span>Success rate</span><strong>{successRate}%</strong></div><div><span>Avg. duration</span><strong>{duration(overallAverage)}</strong></div><div><span>Total runs</span><strong>{totalRuns}</strong></div></div>
            <div className="mini-charts"><ResponsiveContainer width="58%" height={130}><BarChart data={executionData}><XAxis dataKey="name" tick={{ fill: "#a6a4b9", fontSize: 8 }} axisLine={false} tickLine={false} /><YAxis hide /><Tooltip formatter={(value) => [duration(value), "Average time"]} contentStyle={{ background: "#161829", border: "1px solid #393653", borderRadius: 8 }} /><Bar dataKey="time" radius={[5, 5, 0, 0]} fill="#a99dff" /></BarChart></ResponsiveContainer><ResponsiveContainer width="42%" height={130}><PieChart><Pie data={successData} dataKey="value" innerRadius={34} outerRadius={51} paddingAngle={3}>{successData.map((entry, index) => <Cell key={entry.name} fill={index === 0 ? "#78e4bd" : "#ff9587"} />)}</Pie><Tooltip contentStyle={{ background: "#161829", border: "1px solid #393653", borderRadius: 8 }} /></PieChart></ResponsiveContainer></div>
          </article>
        </div>

        <div className="agent-summary-table"><div className="subsection-heading"><h3>Agent execution summary</h3><span>Grouped by agent</span></div><div className="execution-table-wrap"><table><thead><tr><th>Agent Name</th><th>Last Execution Time</th><th>Average Execution Time</th><th>Total Runs</th><th>Latest Status</th></tr></thead><tbody>{summaries.map((summary) => <tr key={summary.name}><td>{summary.name}</td><td>{summary.latest ? duration(summary.latest.execution_time) : "—"}</td><td>{duration(summary.average)}</td><td>{summary.runs}</td><td><span className={`badge trace-${isSuccess(summary.status) ? "success" : "failed"}`}>{summary.status}</span></td></tr>)}</tbody></table></div></div>
        <details className="raw-execution-logs"><summary>View Raw Execution Logs <span>Latest 10 records</span></summary><div className="execution-table-wrap"><table><thead><tr><th>Agent</th><th>Execution Time</th><th>Status</th><th>Timestamp</th></tr></thead><tbody>{latest.length === 0 ? <tr><td colSpan="4" className="empty-state">No executions available.</td></tr> : latest.map((trace, index) => <tr key={`${trace.agent_name}-${trace.created_at}-${index}`}><td>{trace.agent_name || "Agent"}</td><td><Clock3 size={13} /> {duration(trace.execution_time)}</td><td><span className={`badge trace-${isSuccess(trace.status) ? "success" : "failed"}`}>{trace.status || "UNKNOWN"}</span></td><td>{dateTime(trace.created_at)}</td></tr>)}</tbody></table></div></details>
      </>}
    </section>
  );
}


