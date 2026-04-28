from __future__ import annotations

from typing import AsyncIterator

from ....domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse


class GroqAdapter(LLMPort):
    """Implements LLMPort using Groq's ultra-fast inference API.

    For CLASSIFICATION, EXTRACTION, SIMPLE_QA task types in production.
    """

    DEFAULT_MODEL = "llama3-8b-8192"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._api_key = api_key
        self._model = model
        # TODO: init groq client when dependency is added

    async def complete(self, request: LLMRequest) -> LLMResponse:
        # TODO: implement
        raise NotImplementedError

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        # TODO: implement
        raise NotImplementedError
        yield

    async def health_check(self) -> bool:
        # TODO: implement
        raise NotImplementedError
