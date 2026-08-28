const dateTime = (value) => (value ? new Date(value).toLocaleString() : "—");

export default function MerchantHistory({ history, loading, error }) {
  return <section className="panel"><div className="panel-heading"><div><p className="eyebrow">AUDIT TRAIL</p><h2>Merchant history</h2></div></div>{loading && <p className="section-status">Loading merchant history...</p>}{error && <p className="section-error">{error}</p>}{!loading && !error && <div className="history-list">{history.length === 0 ? <p className="empty-state">No historical analyses are available.</p> : history.map((item) => <article className="history-item" key={item.id}><span className="history-marker" /><div><span className="history-id">Analysis #{item.id}</span><strong>{item.decision}</strong><p>{dateTime(item.created_at)}</p></div><span className={`badge risk-${String(item.risk_level || "").toLowerCase()}`}>{item.risk_level}</span></article>)}</div>}</section>;
}
