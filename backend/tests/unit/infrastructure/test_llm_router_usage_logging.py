from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.ports.llm_port import LLMRequest, LLMResponse, LLMTaskType
from src.infrastructure.llm_router.llm_router import LLMRouter


def _make_response(provider: str = "anthropic") -> LLMResponse:
    return LLMResponse(
        content="ok",
        model="claude-sonnet-4-6",
        provider=provider,
        input_tokens=100,
        output_tokens=50,
    )


def _make_router(usage_logger=None, fail: bool = False) -> LLMRouter:
    provider = AsyncMock()
    if fail:
        provider.complete.side_effect = RuntimeError("provider down")
    else:
        provider.complete.return_value = _make_response()
    return LLMRouter(ollama=provider, retry_attempts=1, usage_logger=usage_logger)


class TestLLMRouterUsageLogging:
    @pytest.mark.asyncio
    async def test_logs_on_successful_complete(self) -> None:
        logger = AsyncMock()
        router = _make_router(usage_logger=logger)
        req = LLMRequest(prompt="hi", task_type=LLMTaskType.SIMPLE_QA)

        with patch("asyncio.create_task") as mock_task:
            await router.complete(req)
            mock_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_log_when_usage_logger_is_none(self) -> None:
        router = _make_router(usage_logger=None)
        req = LLMRequest(prompt="hi", task_type=LLMTaskType.SIMPLE_QA)

        with patch("asyncio.create_task") as mock_task:
            await router.complete(req)
            mock_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_response_even_with_logger(self) -> None:
        logger = AsyncMock()
        router = _make_router(usage_logger=logger)
        req = LLMRequest(prompt="hi", task_type=LLMTaskType.SIMPLE_QA)

        with patch("asyncio.create_task"):
            resp = await router.complete(req)

        assert resp.provider == "anthropic"
        assert resp.input_tokens == 100

    @pytest.mark.asyncio
    async def test_no_log_on_provider_failure(self) -> None:
        logger = AsyncMock()
        router = _make_router(usage_logger=logger, fail=True)
        req = LLMRequest(prompt="hi", task_type=LLMTaskType.SIMPLE_QA)

        with patch("asyncio.create_task") as mock_task:
            with pytest.raises(RuntimeError):
                await router.complete(req)
            mock_task.assert_not_called()


class TestLLMUsageCostEstimation:
    def test_known_model_returns_cost(self) -> None:
        from src.adapters.secondary.persistence.llm_usage_adapter import _estimate_cost
        cost = _estimate_cost("claude-sonnet-4-6", 1_000_000, 1_000_000)
        assert cost == pytest.approx(18.0)

    def test_unknown_model_returns_none(self) -> None:
        from src.adapters.secondary.persistence.llm_usage_adapter import _estimate_cost
        assert _estimate_cost("gpt-4", 100, 100) is None

    def test_ollama_not_in_table(self) -> None:
        from src.adapters.secondary.persistence.llm_usage_adapter import _estimate_cost
        assert _estimate_cost("llama3.2", 500, 200) is None

    def test_groq_llama_cost(self) -> None:
        from src.adapters.secondary.persistence.llm_usage_adapter import _estimate_cost
        cost = _estimate_cost("llama3-8b-8192", 1_000_000, 1_000_000)
        assert cost is not None
        assert cost > 0
