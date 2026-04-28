from __future__ import annotations

from typing import AsyncIterator

import anthropic

from ....domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse


class ClaudeAdapter(LLMPort):
    """Implements LLMPort using the Anthropic Claude API.

    For REASONING and GENERATION_LONG task types.
    All calls go through the LLMRouter — never call this adapter directly from use cases.
    """

    DEFAULT_MODEL = "claude-sonnet-4-6"
    HAIKU_MODEL = "claude-haiku-4-5-20251001"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete(self, request: LLMRequest) -> LLMResponse:
        # TODO: implement — call self._client.messages.create()
        # Apply circuit breaker via tenacity (done in LLMRouter wrapper)
        raise NotImplementedError

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        # TODO: implement — use self._client.messages.stream() context manager
        raise NotImplementedError
        yield  # make this a generator stub

    async def health_check(self) -> bool:
        # TODO: implement — lightweight ping to Anthropic API
        raise NotImplementedError
