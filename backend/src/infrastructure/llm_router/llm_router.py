from __future__ import annotations

import logging
from typing import AsyncIterator

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ...domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse, LLMTaskType
from ..config.settings import LLMMode, settings
from .task_classifier import TaskClassifier

logger = logging.getLogger(__name__)


CLOUD_REASONING_TYPES = {LLMTaskType.REASONING, LLMTaskType.GENERATION_LONG}
FAST_TYPES = {LLMTaskType.CLASSIFICATION, LLMTaskType.EXTRACTION, LLMTaskType.SIMPLE_QA}


class LLMRouter(LLMPort):
    """Routes LLM requests to the optimal provider based on task type and availability.

    Priority order (HYBRID/CLOUD mode):
      REASONING / GENERATION_LONG → Claude → Groq → Ollama
      CLASSIFICATION / EXTRACTION / SIMPLE_QA → Groq → Ollama → Claude
    In LOCAL mode, all requests go to Ollama.

    Every provider call is wrapped in a tenacity retry+circuit-breaker pattern.
    """

    def __init__(
        self,
        claude: LLMPort | None,
        groq: LLMPort | None,
        gemini: LLMPort | None,
        ollama: LLMPort,
        mode: LLMMode = settings.llm_mode,
    ) -> None:
        self._claude = claude
        self._groq = groq
        self._gemini = gemini
        self._ollama = ollama
        self._mode = mode
        self._classifier = TaskClassifier()

    def _resolve_provider(self, task_type: LLMTaskType) -> list[LLMPort]:
        """Returns ordered list of providers to try for this task type."""
        if self._mode == LLMMode.LOCAL:
            return [self._ollama]

        if task_type in CLOUD_REASONING_TYPES:
            candidates = [self._claude, self._gemini, self._ollama]
        else:
            candidates = [self._groq, self._ollama, self._claude]

        return [p for p in candidates if p is not None]

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def complete(self, request: LLMRequest) -> LLMResponse:
        providers = self._resolve_provider(request.task_type)
        last_error: Exception | None = None
        for provider in providers:
            try:
                return await provider.complete(request)
            except Exception as exc:
                logger.warning("Provider %s failed: %s", provider.__class__.__name__, exc)
                last_error = exc
        raise last_error or RuntimeError("No LLM provider available")

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        # Streaming always uses the first available cloud provider or Ollama
        providers = self._resolve_provider(request.task_type)
        for provider in providers:
            try:
                async for token in provider.stream(request):
                    yield token
                return
            except Exception as exc:
                logger.warning("Stream provider %s failed: %s", provider.__class__.__name__, exc)
        raise RuntimeError("No LLM provider available for streaming")

    async def health_check(self) -> bool:
        # Returns True if at least one provider is healthy
        for provider in [self._ollama, self._claude, self._groq, self._gemini]:
            if provider and await provider.health_check():
                return True
        return False
