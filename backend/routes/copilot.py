import json
import uuid
import os
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, List
from pydantic import BaseModel

# Import services
from backend.services.chat_history_service import chat_history_service
from backend.services.ollama_streaming_service import ollama_streaming_service
from backend.services.file_parser_service import file_parser_service
from backend.services.rag_service import rag_service
from backend.settings import ALLOWED_EXTENSIONS, UPLOAD_DIR

router = APIRouter(tags=["Copilot Upgrade"])

# Personalities System Prompts
PERSONALITY_PROMPTS = {
    "analyst": (
        "You are an elite Business Analyst. Focus on transaction volume, growth trends, seasonal drift, "
        "and operational telemetry. Provide quantitative metrics, unit economics, and data-driven insights."
    ),
    "risk": (
        "You are an expert Payment Gateway Risk Analyst. Focus on fraud vectors, transaction velocities, "
        "refund velocities, chargeback rates, and buyer retention indicators. Highlight potential vulnerabilities "
        "and fraud thresholds."
    ),
    "underwriter": (
        "You are a Senior Risk Underwriter. Focus on creditworthiness, KYC authenticity, merchant default probability, "
        "settlement velocity, and compliance limits. Your style is objective, precise, and regulatory-focused."
    ),
    "growth": (
        "You are a Strategic Growth Consultant. Focus on revenue optimization, payment authorization success rate boost, "
        "checkout conversion rates, checkout speed, and churn reduction strategies. Propose high-ROI interventions."
    ),
    "general": (
        "You are a helpful, general-purpose AI assistant. Answer general questions, write clean and optimized code, "
        "and help the user with any tasks. You behave like ChatGPT or Claude."
    )
}

# Request Schemas
class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"
    mode: str = "general" # 'merchant' | 'general'
    personality: str = "general" # 'analyst' | 'risk' | 'underwriter' | 'growth' | 'general'
    merchant_id: Optional[str] = None
    model_used: Optional[str] = None

class RenameConversationRequest(BaseModel):
    title: str

class ChatStreamRequest(BaseModel):
    conversation_id: str
    question: str
    model_name: Optional[str] = None

# --- REST Endpoints for SQLite History ---

@router.get("/copilot/conversations")
def get_conversations(search: Optional[str] = Query(None, description="Search term for query")):
    if search:
        return chat_history_service.search_conversations_and_messages(search)
    return chat_history_service.list_conversations()

@router.post("/copilot/conversations")
def create_conversation(req: CreateConversationRequest):
    conv_id = str(uuid.uuid4())
    return chat_history_service.create_conversation(
        conv_id=conv_id,
        title=req.title,
        mode=req.mode,
        personality=req.personality,
        merchant_id=req.merchant_id,
        model_used=req.model_used
    )

@router.put("/copilot/conversations/{conversation_id}")
def rename_conversation(conversation_id: str, req: RenameConversationRequest):
    chat_history_service.update_conversation_title(conversation_id, req.title)
    return {"status": "success"}

@router.delete("/copilot/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    chat_history_service.delete_conversation(conversation_id)
    return {"status": "success"}

@router.delete("/copilot/conversations")
def clear_conversations():
    chat_history_service.clear_all_conversations()
    return {"status": "success"}

@router.get("/copilot/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str):
    return chat_history_service.get_messages(conversation_id)

# --- Stop Generation Endpoint ---
@router.post("/copilot/chat/stop")
def stop_chat_generation(req: ChatStreamRequest):
    ollama_streaming_service.stop_generation(req.conversation_id)
    return {"status": "stopped"}

# --- Model Detection Endpoint ---
@router.get("/copilot/models")
async def get_ollama_models(sync: bool = Query(False, description="Sync models dynamically with Ollama daemon")):
    if sync:
        models = await ollama_streaming_service.list_local_models()
    else:
        models = ollama_streaming_service._cached_models
        if not models:
            # High-performance instant default list
            models = ["qwen2.5:3b", "llama3.1", "qwen2.5:latest", "llama3.2"]
            
    # Determine default without querying Ollama again
    from backend.settings import PREFERRED_MODELS
    active_default = "qwen2.5:3b"
    
    if models:
        for pref in PREFERRED_MODELS:
            for inst in models:
                if inst == pref or inst.startswith(pref + ":"):
                    active_default = inst
                    break
            else:
                continue
            break
        if not active_default and models:
            active_default = models[0]

    return {
        "status": "online" if (sync or ollama_streaming_service._cached_models) else "cached",
        "models": models,
        "active_default": active_default
    }

# --- File Upload Endpoint ---
@router.post("/copilot/upload")
async def upload_file_analysis(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed. Select TXT, PDF, CSV, or XLSX.")
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        parsed = file_parser_service.parse_file(temp_path)
        return {
            "status": "success",
            "file_name": file.filename,
            "parsed_summary": parsed["summary"],
            "text_content": parsed["text_content"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload processing failed: {str(e)}")
    finally:
        # Clean up local scratch copy
        if os.path.exists(temp_path):
            os.remove(temp_path)

# --- SSE Chat Streaming Endpoint ---
@router.post("/copilot/chat/stream")
async def stream_chat_tokens(req: ChatStreamRequest):
    conversation = chat_history_service.get_conversation(req.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    mode = conversation["mode"]
    personality = conversation["personality"]
    merchant_id = conversation["merchant_id"]
    model_to_use = req.model_name or conversation["model_used"] or "qwen2.5:3b"

    # 1. Fetch Past Messages (Conversation Memory)
    past_messages = chat_history_service.get_messages(req.conversation_id)
    
    # 2. Compile System Prompt & RAG context
    system_prompt_parts = []
    
    # AI Personality Prompt
    system_prompt_parts.append(PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS["general"]))
    
    agents_consulted = []
    rag_context_text = ""

    # RAG Context Retrieval for Merchant Mode
    if mode == "merchant" and merchant_id:
        rag_data = rag_service.retrieve_merchant_context(merchant_id)
        if rag_data["merchant_found"]:
            rag_context_text = rag_data["formatted_text"]
            agents_consulted = rag_data["agents_consulted"]
            system_prompt_parts.append(
                f"\nGround your response strictly in this live retrieved merchant intelligence ledger:\n{rag_context_text}"
            )
        else:
            system_prompt_parts.append(f"\n[Warning] Merchant ID {merchant_id} was not found in postgres tables.")

    system_context = "\n".join(system_prompt_parts)

    # 3. Save User Message to SQLite
    user_msg_id = str(uuid.uuid4())
    chat_history_service.add_message(
        msg_id=user_msg_id,
        conv_id=req.conversation_id,
        role="user",
        content=req.question,
        model_used=model_to_use
    )

    # 4. Form message list for Ollama
    messages_payload = []
    
    # Inject System Context
    if system_context:
        messages_payload.append({"role": "system", "content": system_context})
        
    # Append past message logs
    for msg in past_messages:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})
        
    # Append current query
    messages_payload.append({"role": "user", "content": req.question})

    # Generator wrapper to capture full response and write to SQLite when finished
    async def sse_generator():
        full_assistant_content = []
        tokens_count = 0
        latency = 0.0
        final_model = model_to_use

        async for chunk in ollama_streaming_service.stream_chat(
            conversation_id=req.conversation_id,
            messages=messages_payload,
            model=model_to_use
        ):
            yield chunk
            
            # Check SSE line formatting
            if chunk.startswith("data: "):
                try:
                    payload = json.loads(chunk[6:].strip())
                    # Accumulate token content
                    if "token" in payload:
                        full_assistant_content.append(payload["token"])
                    # Save metrics on complete
                    elif payload.get("event") == "done":
                        tokens_count = payload.get("tokens", 0)
                        latency = payload.get("latency", 0.0)
                        final_model = payload.get("model", model_to_use)
                except Exception:
                    pass

        # Save assistant message to SQLite
        assistant_content_str = "".join(full_assistant_content)
        if assistant_content_str:
            assistant_msg_id = str(uuid.uuid4())
            chat_history_service.add_message(
                msg_id=assistant_msg_id,
                conv_id=req.conversation_id,
                role="assistant",
                content=assistant_content_str,
                tokens=tokens_count,
                latency=latency,
                agents_consulted=agents_consulted,
                model_used=final_model
            )
            # Automatic chat title generation on first message
            if len(past_messages) == 0:
                # Truncate first question to 35 chars
                auto_title = req.question[:35] + ("..." if len(req.question) > 35 else "")
                chat_history_service.update_conversation_title(req.conversation_id, auto_title)

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

# --- Export Conversation Endpoint ---
@router.get("/copilot/conversations/{conversation_id}/export")
def export_conversation(conversation_id: str, format: str = Query("md")):
    conversation = chat_history_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
        
    messages = chat_history_service.get_messages(conversation_id)
    title_safe = "".join([c if c.isalnum() else "_" for c in conversation["title"]])
    
    if format == "md":
        content = [f"# {conversation['title']}\n"]
        content.append(f"**Mode**: {conversation['mode']} | **Personality**: {conversation['personality']}\n")
        content.append(f"**Created At**: {conversation['created_at']}\n---\n")
        
        for m in messages:
            role = "User" if m["role"] == "user" else "Advisor AI"
            content.append(f"### 👤 {role} ({m['timestamp']})")
            content.append(m["content"] + "\n")
            
        file_path = os.path.join(UPLOAD_DIR, f"{title_safe}.md")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
            
        return FileResponse(file_path, media_type="text/markdown", filename=f"{title_safe}.md")
        
    elif format == "txt":
        content = [f"=== {conversation['title']} ===\n"]
        content.append(f"Mode: {conversation['mode']} | Personality: {conversation['personality']}\n")
        for m in messages:
            role = "USER" if m["role"] == "user" else "ADVISOR"
            content.append(f"[{m['timestamp']}] {role}:")
            content.append(m["content"] + "\n")
            
        file_path = os.path.join(UPLOAD_DIR, f"{title_safe}.txt")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
            
        return FileResponse(file_path, media_type="text/plain", filename=f"{title_safe}.txt")

    elif format == "pdf":
        try:
            # Generate server-side vector PDF using ReportLab
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            os.makedirs(UPLOAD_DIR, exist_ok=True)
            pdf_path = os.path.join(UPLOAD_DIR, f"{title_safe}.pdf")
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor("#6366F1"),
                spaceAfter=12
            )
            meta_style = ParagraphStyle(
                'MetaStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#6B7280"),
                spaceAfter=20
            )
            role_style = ParagraphStyle(
                'RoleStyle',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor("#1F2937"),
                spaceAfter=6,
                spaceBefore=14
            )
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontSize=10.5,
                leading=14,
                textColor=colors.HexColor("#374151")
            )
            
            story.append(Paragraph(conversation['title'], title_style))
            story.append(Paragraph(f"Mode: {conversation['mode']} | Personality: {conversation['personality']} | Date: {conversation['created_at']}", meta_style))
            story.append(Spacer(1, 10))
            
            for m in messages:
                role = "User" if m["role"] == "user" else "Advisor AI"
                story.append(Paragraph(f"{role} ({m['timestamp']})", role_style))
                story.append(Paragraph(m["content"].replace("\n", "<br/>"), body_style))
                
            doc.build(story)
            return FileResponse(pdf_path, media_type="application/pdf", filename=f"{title_safe}.pdf")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF Export failed: {str(e)}")
            
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Select md, txt, or pdf.")


# --- Backward Compatibility Endpoints ---
from agents.copilot_agent import copilot_agent

class CopilotQueryRequest(BaseModel):
    merchant_id: str
    question: str

@router.get("/copilot/{merchant_id}")
def ask_copilot_get(
    merchant_id: str,
    question: str = Query(..., description="User query about merchant risk, revenue, or recommendations")
):
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
    try:
        answer = copilot_agent(merchant_id=payload.merchant_id, question=payload.question)
        return {
            "merchant_id": payload.merchant_id,
            "question": payload.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot query failed: {str(e)}")