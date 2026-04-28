from __future__ import annotations

import httpx
from typing import AsyncIterator

from ....domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse


class OllamaLLMAdapter(LLMPort):
    """Implements LLMPort using a local Ollama instance.

    Used as fallback and in local development (LLM_MODE=local).
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self._base_url = base_url
        self._model = model

    async def complete(self, request: LLMRequest) -> LLMResponse:
        # TODO: implement — POST /api/generate or /api/chat
        raise NotImplementedError

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        # TODO: implement — POST /api/generate with stream=true
        raise NotImplementedError
        yield

    async def health_check(self) -> bool:
        # TODO: implement — GET /api/tags to verify Ollama is running
        raise NotImplementedError
