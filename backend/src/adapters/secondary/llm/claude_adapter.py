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

    def _build_kwargs(self, request: LLMRequest) -> dict:
        system = request.system or ""
        if request.json_mode:
            json_instruction = "Respond only with valid JSON. Do not include any text outside the JSON."
            system = f"{system}\n{json_instruction}".strip()

        kwargs: dict = {
            "model": self._model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        if system:
            kwargs["system"] = system
        return kwargs

    async def complete(self, request: LLMRequest) -> LLMResponse:
        response = await self._client.messages.create(**self._build_kwargs(request))
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            provider="anthropic",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        async with self._client.messages.stream(**self._build_kwargs(request)) as s:
            async for token in s.text_stream:
                yield token

    async def health_check(self) -> bool:
        try:
            await self._client.messages.create(
                model=self.HAIKU_MODEL,
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False
