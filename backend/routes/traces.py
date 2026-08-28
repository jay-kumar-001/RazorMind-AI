from fastapi import APIRouter, Query
import json
import logging
from backend.database import SessionLocal
from backend.models import AgentExecution

logger = logging.getLogger("razormind.traces")
router = APIRouter(tags=["Observability"])


def save_agent_trace(
    merchant_id: str,
    agent_name: str,
    execution_time: float,
    status: str = "SUCCESS",
    input_query: str = "",
    output_summary: str = "",
    confidence: float = None,
    reasoning: str = "",
    source_metrics: dict = None,
):
    payload = {
        "input": input_query if not isinstance(input_query, dict) else input_query,
        "confidence": confidence,
        "reasoning": reasoning,
        "source_metrics": source_metrics or {},
    }
    db = SessionLocal()
    try:
        execution = AgentExecution(
            merchant_id=str(merchant_id),
            agent_name=str(agent_name),
            execution_time=round(float(execution_time), 4),
            status=str(status).upper(),
            input_query=json.dumps(payload)[:4000],
            output_summary=str(output_summary)[:2000] if output_summary else "Execution recorded",
        )
        db.add(execution)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to record trace for %s: %s", agent_name, e)
    finally:
        db.close()


def _parse_input(raw: str) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        return {"input": raw}
    return {"input": raw}


def _duration_ms(exec_time: float) -> float:
    t = float(exec_time or 0.0)
    return round(t * 1000.0, 2) if t < 5 else round(t, 2)


@router.get("/agent-traces/{merchant_id}")
def get_traces(merchant_id: str, limit: int = Query(40, ge=1, le=200)):
    db = SessionLocal()
    try:
        traces = (
            db.query(AgentExecution)
            .filter(AgentExecution.merchant_id == merchant_id)
            .order_by(AgentExecution.id.desc())
            .limit(limit)
            .all()
        )
        out = []
        for t in traces:
            parsed = _parse_input(t.input_query)
            out.append({
                "id": t.id,
                "merchant_id": t.merchant_id,
                "agent_name": t.agent_name,
                "node_name": (t.agent_name or "").replace(" Agent", ""),
                "execution_time_ms": _duration_ms(t.execution_time),
                "duration_ms": _duration_ms(t.execution_time),
                "execution_time": t.execution_time,
                "status": t.status or "SUCCESS",
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "output_summary": t.output_summary,
                "input": parsed.get("input") or parsed.get("source_metrics") or merchant_id,
                "confidence": parsed.get("confidence"),
                "reasoning": parsed.get("reasoning") or t.output_summary,
                "source_metrics": parsed.get("source_metrics") or {},
            })
        return out
    finally:
        db.close()


@router.get("/traces/summary")
def get_trace_analytics(merchant_id: str = Query(None)):
    db = SessionLocal()
    try:
        from backend.models import MerchantAnalysis
        q = db.query(AgentExecution)
        if merchant_id:
            q = q.filter(AgentExecution.merchant_id == merchant_id)
        traces = q.order_by(AgentExecution.id.desc()).limit(400).all()
        total_runs = len(traces)
        analyses = db.query(MerchantAnalysis).count()
        if total_runs == 0:
            return {
                "total_runs": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "total_analyses": analyses,
                "avg_confidence": None,
                "total_agents": 0,
            }
        success_count = sum(1 for t in traces if str(t.status).upper() in ["SUCCESS", "COMPLETED"])
        avg_time = sum(float(t.execution_time or 0) for t in traces) / total_runs
        confs = []
        for t in traces:
            parsed = _parse_input(t.input_query)
            if parsed.get("confidence") is not None:
                confs.append(float(parsed["confidence"]))
        agents = {t.agent_name for t in traces if t.agent_name}
        return {
            "total_runs": total_runs,
            "successful_runs": success_count,
            "success_rate": round((success_count / total_runs) * 100.0, 1),
            "avg_duration_ms": _duration_ms(avg_time),
            "total_analyses": analyses,
            "avg_confidence": round(sum(confs) / len(confs), 1) if confs else None,
            "total_agents": len(agents),
        }
    finally:
        db.close()
