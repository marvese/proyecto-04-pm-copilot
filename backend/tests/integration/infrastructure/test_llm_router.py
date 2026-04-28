from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from src.infrastructure.llm_router.llm_router import LLMRouter
from src.domain.ports.llm_port import LLMRequest, LLMTaskType
from src.infrastructure.config.settings import LLMMode


class TestLLMRouter:
    @pytest.mark.asyncio
    async def test_local_mode_uses_ollama_only(self) -> None:
        ollama = AsyncMock()
        ollama.complete.return_value = AsyncMock(content="ok", model="llama3", provider="ollama", input_tokens=10, output_tokens=5)

        router = LLMRouter(claude=None, groq=None, gemini=None, ollama=ollama, mode=LLMMode.LOCAL)
        request = LLMRequest(prompt="hello", task_type=LLMTaskType.SIMPLE_QA)
        await router.complete(request)

        ollama.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_to_ollama_when_claude_fails(self) -> None:
        claude = AsyncMock()
        claude.complete.side_effect = RuntimeError("API down")
        ollama = AsyncMock()
        ollama.complete.return_value = AsyncMock(content="fallback", model="llama3", provider="ollama", input_tokens=10, output_tokens=5)

        router = LLMRouter(claude=claude, groq=None, gemini=None, ollama=ollama, mode=LLMMode.HYBRID)
        request = LLMRequest(prompt="analyze this", task_type=LLMTaskType.REASONING)
        # TODO: once LLMRouter fallback is fully implemented this should succeed
        pytest.skip("Not implemented yet")
