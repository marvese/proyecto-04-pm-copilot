from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from src.domain.ports.llm_port import LLMPort, LLMRequest, LLMResponse, LLMTaskType
from src.infrastructure.llm_router.llm_router import LLMRouter
from src.infrastructure.config.settings import LLMMode


def make_response(provider: str = "mock") -> LLMResponse:
    return LLMResponse(
        content="ok", model="test", provider=provider, input_tokens=10, output_tokens=5
    )


def make_request(task_type: LLMTaskType = LLMTaskType.SIMPLE_QA) -> LLMRequest:
    return LLMRequest(prompt="hello", task_type=task_type)


def mock_provider(provider_name: str = "mock", *, fails: bool = False) -> AsyncMock:
    m = AsyncMock(spec=LLMPort)
    if fails:
        m.complete.side_effect = RuntimeError(f"{provider_name} unavailable")
    else:
        m.complete.return_value = make_response(provider_name)
    m.health_check.return_value = not fails
    return m


# retry_attempts=1 disables tenacity backoff waits in all tests
def make_router(**kwargs) -> LLMRouter:
    return LLMRouter(retry_attempts=1, **kwargs)


class TestLocalMode:
    async def test_local_mode_uses_ollama_only(self):
        ollama = mock_provider("ollama")
        claude = mock_provider("claude")
        router = make_router(ollama=ollama, claude=claude, mode=LLMMode.LOCAL)

        result = await router.complete(make_request(LLMTaskType.REASONING))

        ollama.complete.assert_awaited_once()
        claude.complete.assert_not_awaited()
        assert result.provider == "ollama"

    async def test_local_mode_classification_also_uses_ollama(self):
        ollama = mock_provider("ollama")
        router = make_router(ollama=ollama, mode=LLMMode.LOCAL)

        result = await router.complete(make_request(LLMTaskType.CLASSIFICATION))

        ollama.complete.assert_awaited_once()
        assert result.provider == "ollama"


class TestHybridModeFallback:
    async def test_fallback_to_ollama_when_claude_fails(self):
        claude = mock_provider("claude", fails=True)
        ollama = mock_provider("ollama")
        router = make_router(ollama=ollama, claude=claude, mode=LLMMode.HYBRID)

        result = await router.complete(make_request(LLMTaskType.REASONING))

        claude.complete.assert_awaited_once()
        ollama.complete.assert_awaited_once()
        assert result.provider == "ollama"

    async def test_reasoning_uses_claude_first_when_available(self):
        claude = mock_provider("claude")
        ollama = mock_provider("ollama")
        router = make_router(ollama=ollama, claude=claude, mode=LLMMode.HYBRID)

        result = await router.complete(make_request(LLMTaskType.REASONING))

        claude.complete.assert_awaited_once()
        ollama.complete.assert_not_awaited()
        assert result.provider == "claude"

    async def test_classification_uses_groq_first(self):
        groq = mock_provider("groq")
        ollama = mock_provider("ollama")
        claude = mock_provider("claude")
        router = make_router(ollama=ollama, groq=groq, claude=claude, mode=LLMMode.HYBRID)

        result = await router.complete(make_request(LLMTaskType.CLASSIFICATION))

        groq.complete.assert_awaited_once()
        ollama.complete.assert_not_awaited()
        assert result.provider == "groq"

    async def test_classification_falls_back_to_ollama_when_groq_fails(self):
        groq = mock_provider("groq", fails=True)
        ollama = mock_provider("ollama")
        router = make_router(ollama=ollama, groq=groq, mode=LLMMode.HYBRID)

        result = await router.complete(make_request(LLMTaskType.CLASSIFICATION))

        groq.complete.assert_awaited_once()
        ollama.complete.assert_awaited_once()
        assert result.provider == "ollama"

    async def test_no_providers_for_reasoning_falls_back_to_ollama(self):
        """HYBRID with claude=None should fall back to ollama for reasoning tasks."""
        ollama = mock_provider("ollama")
        router = make_router(ollama=ollama, mode=LLMMode.HYBRID)

        result = await router.complete(make_request(LLMTaskType.REASONING))

        assert result.provider == "ollama"


class TestAllProvidersFail:
    async def test_all_providers_fail_raises(self):
        claude = mock_provider("claude", fails=True)
        ollama = mock_provider("ollama", fails=True)
        router = make_router(ollama=ollama, claude=claude, mode=LLMMode.HYBRID)

        with pytest.raises(RuntimeError):
            await router.complete(make_request(LLMTaskType.REASONING))

    async def test_local_mode_ollama_fails_raises(self):
        ollama = mock_provider("ollama", fails=True)
        router = make_router(ollama=ollama, mode=LLMMode.LOCAL)

        with pytest.raises(RuntimeError):
            await router.complete(make_request())


class TestStreaming:
    async def test_stream_yields_tokens_from_provider(self):
        async def token_gen(*_):
            for t in ["hello", " ", "world"]:
                yield t

        ollama = mock_provider("ollama")
        ollama.stream = token_gen
        router = make_router(ollama=ollama, mode=LLMMode.LOCAL)

        tokens = []
        async for token in router.stream(make_request()):
            tokens.append(token)

        assert tokens == ["hello", " ", "world"]

    async def test_stream_falls_back_when_first_provider_fails(self):
        async def failing_gen(*_):
            raise RuntimeError("stream error")
            yield  # make it a generator

        async def ok_gen(*_):
            yield "fallback"

        claude = mock_provider("claude")
        claude.stream = failing_gen
        ollama = mock_provider("ollama")
        ollama.stream = ok_gen
        router = make_router(ollama=ollama, claude=claude, mode=LLMMode.HYBRID)

        tokens = []
        async for token in router.stream(make_request(LLMTaskType.REASONING)):
            tokens.append(token)

        assert tokens == ["fallback"]

    async def test_stream_raises_when_all_providers_fail(self):
        async def failing_gen(*_):
            raise RuntimeError("stream error")
            yield

        ollama = mock_provider("ollama")
        ollama.stream = failing_gen
        router = make_router(ollama=ollama, mode=LLMMode.LOCAL)

        with pytest.raises(RuntimeError, match="No LLM provider available for streaming"):
            async for _ in router.stream(make_request()):
                pass


class TestHealthCheck:
    async def test_healthy_when_at_least_one_provider_ok(self):
        ollama = mock_provider("ollama", fails=True)
        claude = mock_provider("claude")
        router = make_router(ollama=ollama, claude=claude, mode=LLMMode.HYBRID)

        assert await router.health_check() is True

    async def test_unhealthy_when_all_fail(self):
        ollama = mock_provider("ollama", fails=True)
        router = make_router(ollama=ollama, mode=LLMMode.LOCAL)

        assert await router.health_check() is False
