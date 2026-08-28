import { Eye } from "lucide-react";

const dateTime = (value) => (value ? new Date(value).toLocaleString() : "—");
const classNameFor = (value) => String(value || "").toLowerCase().replaceAll(" ", "-");

export default function RecentAnalysesTable({ analyses, loading, error, onViewReport }) {
  return (
    <section className="panel">
      <div className="panel-heading"><div><p className="eyebrow">ACTIVITY</p><h2>Recent analyses</h2></div></div>
      {loading && <p className="section-status">Loading recent analyses...</p>}
      {error && <p className="section-error">{error}</p>}
      {!loading && !error && <div className="table-scroll"><table>
        <thead><tr><th>Analysis ID</th><th>Merchant ID</th><th>Decision</th><th>Risk Level</th><th>Created At</th><th>Actions</th></tr></thead>
        <tbody>{analyses.length === 0 ? <tr><td colSpan="6" className="empty-state">No analyses are available yet.</td></tr> : analyses.map((analysis) => (
          <tr key={analysis.id}><td>#{analysis.id}</td><td>{analysis.merchant_id}</td><td><span className={`badge decision-${classNameFor(analysis.decision)}`}>{analysis.decision}</span></td><td><span className={`badge risk-${classNameFor(analysis.risk_level)}`}>{analysis.risk_level}</span></td><td>{dateTime(analysis.created_at)}</td><td><button className="small-button" onClick={() => onViewReport(analysis.id)}><Eye size={14} />View Report</button></td></tr>
        ))}</tbody>
      </table></div>}
    </section>
  );
}
