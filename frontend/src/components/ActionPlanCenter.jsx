import { CheckCircle2, Circle, Target } from "lucide-react";
import ReactMarkdown from "react-markdown";

const weeks = ["Week 1", "Week 2", "Week 3", "Week 4"];

export default function ActionPlanCenter({ plan, loading, error, onGenerate }) {
  const text = plan?.action_plan || "";
  const steps = weeks.map((week) => ({
    week,
    complete: text.toLowerCase().includes(week.toLowerCase())
  }));

  return (
    <section className="panel full-panel action-plan-center">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">30-DAY ROADMAP</p>
          <h2>Action plan center</h2>
        </div>
        <button className="primary-button" onClick={onGenerate}>
          {loading ? "Generating..." : "Generate plan"}
        </button>
      </div>
      {error && <p className="section-error">{error}</p>}
      {!plan && !loading && <p className="empty-state">Generate a tailored 30-day action plan for this merchant.</p>}
      {loading && <p className="section-status">Loading action plan...</p>}
      {plan && <>
        <div className="roadmap-progress">
          {steps.map((step, index) => <div className="roadmap-step" key={step.week}>
            {step.complete ? <CheckCircle2 size={18} /> : <Circle size={18} />}
            <span>{step.week}</span>
            {index < steps.length - 1 && <i />}
          </div>)}
          <div className="outcome-chip"><Target size={16} />Expected outcome</div>
        </div>
        <article className="action-plan-document"><ReactMarkdown>{text}</ReactMarkdown></article>
      </>}
    </section>
  );
}
