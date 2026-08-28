import httpx
import json
import asyncio
import time
import logging
from typing import AsyncGenerator, List, Dict
from backend.settings import PREFERRED_MODELS

logger = logging.getLogger("razormind.ollama.stream")

# Global dict to track cancellation states: {conversation_id: is_cancelled}
CANCELLED_TASKS: Dict[str, bool] = {}

class OllamaStreamingService:
    def __init__(self):
        self.base_url = "http://localhost:11434"

    async def list_local_models(self) -> List[str]:
        """
        Queries local Ollama instance for installed models.
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return models
        except Exception as e:
            logger.warning(f"Ollama offline or tags endpoint unreachable: {e}")
        return []

    async def get_active_model(self, selected_model: str = None) -> str:
        """
        Detects the best model to use based on preferences and availability.
        """
        installed = await self.list_local_models()
        if not installed:
            # Fallback to default
            return "qwen2.5:3b"
            
        if selected_model and selected_model in installed:
            return selected_model

        # Match preference list
        for model in PREFERRED_MODELS:
            # Match exact or base name (e.g. qwen2.5)
            for inst in installed:
                if inst == model or inst.startswith(model + ":"):
                    return inst
                    
        return installed[0]

    async def stream_chat(self, conversation_id: str, messages: list, model: str = None) -> AsyncGenerator[str, None]:
        """
        Streams chat completion tokens from Ollama using Server-Sent Events (SSE).
        """
        # Register task cancellation state
        CANCELLED_TASKS[conversation_id] = False
        
        active_model = await self.get_active_model(model)
        
        # Prepare Ollama payload
        payload = {
            "model": active_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.2
            }
        }
        
        url = f"{self.base_url}/api/chat"
        start_time = time.time()
        token_count = 0

        try:
            # Use httpx streaming client
            async with httpx.AsyncClient(timeout=90.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        yield f"data: {json.dumps({'error': f'Ollama returned status {response.status_code}'})}\n\n"
                        return

                    async for line in response.aiter_lines():
                        # Check for instant cancellation request
                        if CANCELLED_TASKS.get(conversation_id) is True:
                            yield f"data: {json.dumps({'event': 'stop', 'reason': 'cancelled_by_user'})}\n\n"
                            logger.info(f"Stream generation for {conversation_id} interrupted by user.")
                            return
                            
                        if not line:
                            continue
                            
                        try:
                            chunk_data = json.loads(line)
                            token_count += 1
                            
                            # Standard Ollama stream response contains "message": {"content": "..."}
                            content = chunk_data.get("message", {}).get("content", "")
                            is_done = chunk_data.get("done", False)

                            if content:
                                yield f"data: {json.dumps({'token': content})}\n\n"
                                
                            if is_done:
                                latency = time.time() - start_time
                                meta = {
                                    "event": "done",
                                    "model": active_model,
                                    "tokens": token_count,
                                    "latency": round(latency, 2),
                                    "tokens_per_sec": round(token_count / max(0.1, latency), 1)
                                }
                                yield f"data: {json.dumps(meta)}\n\n"
                                break
                        except Exception as e:
                            logger.warning(f"Error parsing Ollama stream chunk: {e}")
                            
        except Exception as e:
            logger.error(f"Ollama stream connection failed: {e}")
            yield f"data: {json.dumps({'error': f'Underwriting advisor service offline. ({str(e)})'})}\n\n"
        finally:
            # Clean up task registry
            if conversation_id in CANCELLED_TASKS:
                del CANCELLED_TASKS[conversation_id]

    def stop_generation(self, conversation_id: str):
        """
        Triggers instant cancellation of active stream.
        """
        if conversation_id in CANCELLED_TASKS:
            CANCELLED_TASKS[conversation_id] = True

ollama_streaming_service = OllamaStreamingService()
