import httpx
import json
import time
import logging
from typing import AsyncGenerator, List, Dict
from backend.settings import PREFERRED_MODELS

logger = logging.getLogger("razormind.ollama.stream")

CANCELLED_TASKS: Dict[str, bool] = {}


class OllamaStreamingService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self._cached_models = []
        self._last_cache_time = 0.0
        self._last_status = "unknown"

    async def list_local_models(self, force: bool = False) -> List[str]:
        if not force and self._cached_models and (time.time() - self._last_cache_time < 15.0):
            return self._cached_models
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m["name"] for m in data.get("models", [])]
                    self._cached_models = models
                    self._last_cache_time = time.time()
                    self._last_status = "online"
                    return models
                self._last_status = "error"
        except Exception as e:
            logger.warning(f"Ollama tags unreachable: {e}")
            self._last_status = "offline"
            if self._cached_models:
                return self._cached_models
        self._cached_models = []
        self._last_cache_time = time.time()
        return []

    async def ping(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                ok = res.status_code == 200
                self._last_status = "online" if ok else "error"
                return ok
        except Exception:
            self._last_status = "offline"
            return False

    async def get_active_model(self, selected_model: str = None) -> str:
        installed = await self.list_local_models()
        if selected_model and selected_model in installed:
            return selected_model
        if selected_model and installed:
            base = selected_model.split(":")[0]
            for inst in installed:
                if inst == selected_model or inst.startswith(base + ":"):
                    return inst
        for model in PREFERRED_MODELS:
            for inst in installed:
                if inst == model or inst.startswith(model.split(":")[0] + ":"):
                    return inst
        if installed:
            return installed[0]
        return selected_model or "qwen2.5:3b"

    async def stream_chat(self, conversation_id: str, messages: list, model: str = None) -> AsyncGenerator[str, None]:
        CANCELLED_TASKS[conversation_id] = False
        active_model = await self.get_active_model(model)

        if not await self.ping():
            yield f"data: {json.dumps({'error': 'ollama_offline', 'message': 'Ollama is offline. Start the daemon and pull a model (e.g. ollama run qwen2.5:3b).'})}\n\n"
            return

        payload = {
            "model": active_model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": 0.2, "num_ctx": 4096, "num_predict": 450},
        }
        url = f"{self.base_url}/api/chat"
        start_time = time.time()
        token_count = 0

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=5.0)) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        body = (await response.aread())[:400].decode("utf-8", errors="ignore")
                        yield f"data: {json.dumps({'error': 'ollama_http', 'message': f'Ollama returned HTTP {response.status_code}. {body}'})}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if CANCELLED_TASKS.get(conversation_id) is True:
                            yield f"data: {json.dumps({'event': 'stop', 'reason': 'cancelled_by_user', 'model': active_model, 'tokens': token_count, 'latency': round(time.time() - start_time, 2)})}\n\n"
                            return

                        if not line:
                            continue

                        try:
                            chunk_data = json.loads(line)
                            content = chunk_data.get("message", {}).get("content", "")
                            is_done = chunk_data.get("done", False)
                            err = chunk_data.get("error")
                            if err:
                                yield f"data: {json.dumps({'error': 'ollama_model', 'message': str(err)})}\n\n"
                                return

                            if content:
                                token_count += 1
                                yield f"data: {json.dumps({'token': content})}\n\n"

                            if is_done:
                                latency = time.time() - start_time
                                yield f"data: {json.dumps({'event': 'done', 'model': active_model, 'tokens': token_count, 'latency': round(latency, 2), 'tokens_per_sec': round(token_count / max(0.1, latency), 1)})}\n\n"
                                return
                        except json.JSONDecodeError:
                            continue
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': 'timeout', 'message': 'The model took too long to respond. Try a smaller model or a shorter question.'})}\n\n"
        except Exception as e:
            logger.error(f"Ollama stream failed: {e}")
            yield f"data: {json.dumps({'error': 'network', 'message': f'Advisor could not reach the local model service. ({str(e)})'})}\n\n"
        finally:
            CANCELLED_TASKS.pop(conversation_id, None)

    def stop_generation(self, conversation_id: str):
        CANCELLED_TASKS[conversation_id] = True


ollama_streaming_service = OllamaStreamingService()
