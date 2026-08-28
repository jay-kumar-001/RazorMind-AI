import { X } from "lucide-react";

const dateTime = (value) => (value ? new Date(value).toLocaleString() : "—");

export default function ExecutiveReportModal({ analysis, loading, error, onClose, open }) {
  if (!open) return null;

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="report-modal" role="dialog" aria-modal="true" aria-labelledby="report-title" onMouseDown={(event) => event.stopPropagation()}>
        <header className="modal-header"><div><p className="eyebrow">EXECUTIVE INTELLIGENCE</p><h2 id="report-title">Analysis report</h2></div><button className="icon-button" onClick={onClose} aria-label="Close report"><X size={20} /></button></header>
        <div className="modal-body">
          {loading && <p className="section-status">Loading report...</p>}
          {error && <p className="section-error">{error}</p>}
          {analysis && <><dl className="report-details"><div><dt>Merchant ID</dt><dd>{analysis.merchant_id}</dd></div><div><dt>Decision</dt><dd>{analysis.decision}</dd></div><div><dt>Risk Level</dt><dd>{analysis.risk_level}</dd></div><div><dt>Created Date</dt><dd>{dateTime(analysis.created_at)}</dd></div></dl><article className="report-copy"><h3>Executive Report</h3><p>{analysis.executive_report || "No executive report was provided for this analysis."}</p></article></>}
        </div>
        <footer className="modal-footer"><button className="primary-button" onClick={onClose}>Close</button></footer>
      </section>
    </div>
  );
}
