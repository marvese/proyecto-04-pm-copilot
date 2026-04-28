from __future__ import annotations

from typing import AsyncIterator

from ....domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse


class GeminiAdapter(LLMPort):
    """Implements LLMPort using Google Gemini API.

    Alternative for very long contexts and multimodal tasks.
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._api_key = api_key
        self._model = model
        # TODO: init google.generativeai client when dependency is added

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
