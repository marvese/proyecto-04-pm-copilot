from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from ....domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse


class OllamaLLMAdapter(LLMPort):
    """Implements LLMPort using a local Ollama instance via HTTP.

    Used as fallback and primary provider in LLM_MODE=local.
    No Anthropic or OpenAI SDK — pure HTTP via httpx.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def _chat_payload(self, request: LLMRequest, *, stream: bool) -> dict:
        messages = [{"role": "user", "content": request.prompt}]
        if request.system:
            messages.insert(0, {"role": "system", "content": request.system})
        return {
            "model": self._model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": request.temperature},
        }

    async def complete(self, request: LLMRequest) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json=self._chat_payload(request, stream=False),
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

        return LLMResponse(
            content=data["message"]["content"],
            model=data.get("model", self._model),
            provider="ollama",
            input_tokens=data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
        )

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/api/chat",
                json=self._chat_payload(request, stream=True),
                timeout=120.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self._base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
