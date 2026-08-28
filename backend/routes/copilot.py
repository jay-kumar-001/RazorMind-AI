from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from agents.copilot_agent import copilot_agent

router = APIRouter(tags=["Copilot"])

class CopilotQueryRequest(BaseModel):
    merchant_id: str
    question: str

@router.get("/copilot/{merchant_id}")
def ask_copilot_get(
    merchant_id: str,
    question: str = Query(..., description="User query about merchant risk, revenue, or recommendations")
):
    """
    Asks RazorMind AI Copilot a question regarding merchant performance.
    """
    try:
        answer = copilot_agent(merchant_id=merchant_id, question=question)
        return {
            "merchant_id": merchant_id,
            "question": question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot query failed: {str(e)}")


@router.post("/copilot/ask")
def ask_copilot_post(payload: CopilotQueryRequest):
    """
    POST endpoint for RazorMind Copilot assistant.
    """
    try:
        answer = copilot_agent(merchant_id=payload.merchant_id, question=payload.question)
        return {
            "merchant_id": payload.merchant_id,
            "question": payload.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot query failed: {str(e)}")