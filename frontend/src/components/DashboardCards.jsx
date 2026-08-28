import { Building2, CheckCircle2, FileSearch, ShieldAlert, Timer } from "lucide-react";

const cards = [
  { key: "total_merchants", label: "Total Merchants", Icon: Building2, tone: "violet" },
  { key: "total_analyses", label: "Total Analyses", Icon: FileSearch, tone: "blue" },
  { key: "approved", label: "Approved", Icon: CheckCircle2, tone: "green" },
  { key: "monitor_closely", label: "Monitor Closely", Icon: Timer, tone: "amber" },
  { key: "high_risk_merchants", label: "High Risk Merchants", Icon: ShieldAlert, tone: "rose" }
];

export default function DashboardCards({ dashboard, loading, error }) {
  if (loading) return <p className="section-status">Loading dashboard metrics...</p>;
  if (error) return <p className="section-error">{error}</p>;

  return (
    <section className="kpi-grid" aria-label="Dashboard metrics">
      {cards.map(({ key, label, Icon, tone }) => (
        <article className={`kpi-card ${tone}`} key={key}>
          <span className="kpi-icon"><Icon size={19} /></span>
          <span className="kpi-label">{label}</span>
          <strong>{Number(dashboard?.[key] ?? 0).toLocaleString()}</strong>
        </article>
      ))}
    </section>
  );
}
