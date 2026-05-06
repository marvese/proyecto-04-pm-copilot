from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, AsyncIterator

from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from ...domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse, LLMTaskType
from ..config.settings import LLMMode, settings

if TYPE_CHECKING:
    from ...adapters.secondary.persistence.llm_usage_adapter import LLMUsageAdapter

logger = logging.getLogger(__name__)

CLOUD_REASONING_TYPES = {LLMTaskType.REASONING, LLMTaskType.GENERATION_LONG}


class LLMRouter(LLMPort):
    """Routes LLM requests to the optimal provider based on task type and availability.

    Priority order (HYBRID/CLOUD mode):
      REASONING / GENERATION_LONG → Claude → Gemini → Ollama
      CLASSIFICATION / EXTRACTION / SIMPLE_QA → Groq → Ollama → Claude
    In LOCAL mode, all requests go to Ollama.

    Tenacity retries the provider chain up to `retry_attempts` times before raising.
    Pass retry_attempts=1 in tests to disable waits.
    """

    def __init__(
        self,
        ollama: LLMPort,
        claude: LLMPort | None = None,
        groq: LLMPort | None = None,
        gemini: LLMPort | None = None,
        mode: LLMMode = settings.llm_mode,
        retry_attempts: int = 3,
        usage_logger: LLMUsageAdapter | None = None,
    ) -> None:
        self._ollama = ollama
        self._claude = claude
        self._groq = groq
        self._gemini = gemini
        self._mode = mode
        self._retry_attempts = retry_attempts
        self._usage_logger = usage_logger

    def _resolve_providers(self, task_type: LLMTaskType) -> list[LLMPort]:
        if self._mode == LLMMode.LOCAL:
            return [self._ollama]

        if task_type in CLOUD_REASONING_TYPES:
            candidates = [self._claude, self._gemini, self._ollama]
        else:
            candidates = [self._groq, self._ollama, self._claude]

        return [p for p in candidates if p is not None]

    async def _try_providers(self, request: LLMRequest) -> LLMResponse:
        providers = self._resolve_providers(request.task_type)
        last_error: Exception | None = None
        for provider in providers:
            try:
                return await provider.complete(request)
            except Exception as exc:
                logger.warning("Provider %s failed: %s", provider.__class__.__name__, exc)
                last_error = exc
        raise last_error or RuntimeError("No LLM provider available")

    async def complete(self, request: LLMRequest) -> LLMResponse:
        t0 = time.monotonic()
        response: LLMResponse | None = None
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        ):
            with attempt:
                response = await self._try_providers(request)

        assert response is not None  # tenacity reraises on failure, so this is always set
        duration_ms = int((time.monotonic() - t0) * 1000)
        if self._usage_logger is not None:
            asyncio.create_task(
                self._usage_logger.log(
                    provider=response.provider,
                    model=response.model,
                    task_type=request.task_type.value,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    duration_ms=duration_ms,
                )
            )
        return response

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        providers = self._resolve_providers(request.task_type)
        for provider in providers:
            try:
                async for token in provider.stream(request):
                    yield token
                return
            except Exception as exc:
                logger.warning("Stream provider %s failed: %s", provider.__class__.__name__, exc)
        raise RuntimeError("No LLM provider available for streaming")

    async def health_check(self) -> bool:
        for provider in [self._ollama, self._claude, self._groq, self._gemini]:
            if provider and await provider.health_check():
                return True
        return False
