import { RefreshCw, ShieldCheck } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import API from "../api/api";

const decisionTone = (decision) => {
  const value = String(decision || "").toUpperCase();
  if (value.includes("APPROVE")) return "approve";
  if (value.includes("REJECT") || value.includes("HIGH RISK") || value.includes("INTERVENTION")) return "reject";
  return "monitor";
};

const reportSection = (report, heading) => {
  if (!report) return "—";
  const headings = "Executive Summary|Revenue Analysis|Risk Assessment|Growth Outlook|Top Recommendations|Final Decision|Confidence Score|Decision Summary";
  const expression = new RegExp(`(?:^|\\n)\\s*${heading}\\s*[:\\n]+([\\s\\S]*?)(?=\\n\\s*(?:${headings})\\s*[:\\n]|$)`, "i");
  return report.match(expression)?.[1]?.trim() || "—";
};

export default function DecisionCenter({ merchantId }) {
  const [data, setData] = useState(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDecision = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const decisionResponse = await API.get(`/decision/${merchantId}`);
      setData(decisionResponse.data);
      try {
        const reportResponse = await API.get(`/executive-report/${merchantId}`);
        setReport(reportResponse.data?.report || "");
      } catch {
        setReport("");
      }
    } catch (requestError) {
      setData(null);
      setError(requestError.response?.data?.detail || "The decision service is temporarily unavailable.");
    } finally {
      setLoading(false);
    }
  }, [merchantId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadDecision();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadDecision]);

  const decision = data?.final_decision;
  const risk = reportSection(report, "Risk Assessment");
  const confidence = reportSection(report, "Confidence Score");
  const summary = reportSection(report, "Decision Summary|Executive Summary");

  return (
    <section className="panel decision-center">
      <div className="panel-heading">
        <div><p className="eyebrow">AI DECISION CENTER</p><h2>Current merchant decision</h2></div>
        <button className="icon-button decision-refresh" onClick={loadDecision} aria-label="Refresh decision"><RefreshCw size={16} /></button>
      </div>
      {loading && <p className="section-status">Loading decision intelligence...</p>}
      {error && <p className="section-error">{error}</p>}
      {!loading && !error && <>
        <div className="decision-hero"><ShieldCheck size={22} /><div><span>Final decision</span><strong className={`decision-badge ${decisionTone(decision)}`}>{decision}</strong></div></div>
        <dl className="decision-details"><div><dt>Risk level</dt><dd>{risk}</dd></div><div><dt>Confidence score</dt><dd>{confidence}</dd></div></dl>
        <article className="decision-summary"><span>Decision summary</span><p>{summary}</p></article>
      </>}
    </section>
  );
}
