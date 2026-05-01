from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.adapters.secondary.llm.claude_adapter import ClaudeAdapter
from src.domain.ports.llm_port import LLMRequest, LLMTaskType


def make_request(prompt: str = "hello", json_mode: bool = False) -> LLMRequest:
    return LLMRequest(
        prompt=prompt,
        task_type=LLMTaskType.REASONING,
        system="Be helpful.",
        max_tokens=256,
        temperature=0.7,
        json_mode=json_mode,
    )


def _mock_anthropic_client() -> MagicMock:
    client = MagicMock()
    client.messages = MagicMock()
    return client


class TestBuildKwargs:
    def test_system_prompt_included(self) -> None:
        adapter = ClaudeAdapter(api_key="test-key")
        kwargs = adapter._build_kwargs(make_request())
        assert kwargs["system"] == "Be helpful."

    def test_json_mode_appends_instruction(self) -> None:
        adapter = ClaudeAdapter(api_key="test-key")
        kwargs = adapter._build_kwargs(make_request(json_mode=True))
        assert "valid JSON" in kwargs["system"]

    def test_no_system_key_when_system_empty(self) -> None:
        adapter = ClaudeAdapter(api_key="test-key")
        req = LLMRequest(prompt="hi", task_type=LLMTaskType.SIMPLE_QA,
                         system=None, max_tokens=10)
        kwargs = adapter._build_kwargs(req)
        assert "system" not in kwargs

    def test_messages_contain_user_prompt(self) -> None:
        adapter = ClaudeAdapter(api_key="test-key")
        kwargs = adapter._build_kwargs(make_request(prompt="my question"))
        assert kwargs["messages"][0] == {"role": "user", "content": "my question"}


class TestComplete:
    async def test_returns_llm_response(self) -> None:
        with patch("anthropic.AsyncAnthropic") as mock_cls:
            mock_client = _mock_anthropic_client()
            mock_cls.return_value = mock_client

            mock_content = MagicMock()
            mock_content.text = "The answer is 42"
            mock_usage = MagicMock()
            mock_usage.input_tokens = 20
            mock_usage.output_tokens = 8
            mock_response = MagicMock()
            mock_response.content = [mock_content]
            mock_response.model = "claude-sonnet-4-6"
            mock_response.usage = mock_usage
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            adapter = ClaudeAdapter(api_key="test-key")
            result = await adapter.complete(make_request())

        assert result.content == "The answer is 42"
        assert result.provider == "anthropic"
        assert result.input_tokens == 20
        assert result.output_tokens == 8

    async def test_complete_calls_create_with_correct_model(self) -> None:
        with patch("anthropic.AsyncAnthropic") as mock_cls:
            mock_client = _mock_anthropic_client()
            mock_cls.return_value = mock_client
            mock_content = MagicMock(text="ok")
            mock_response = MagicMock(content=[mock_content], model="claude-sonnet-4-6",
                                      usage=MagicMock(input_tokens=1, output_tokens=1))
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            adapter = ClaudeAdapter(api_key="test-key", model="claude-sonnet-4-6")
            await adapter.complete(make_request())

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-6"


class TestHealthCheck:
    async def test_returns_true_when_api_responds(self) -> None:
        with patch("anthropic.AsyncAnthropic") as mock_cls:
            mock_client = _mock_anthropic_client()
            mock_cls.return_value = mock_client
            mock_client.messages.create = AsyncMock(return_value=MagicMock())

            adapter = ClaudeAdapter(api_key="test-key")
            result = await adapter.health_check()

        assert result is True

    async def test_returns_false_on_exception(self) -> None:
        with patch("anthropic.AsyncAnthropic") as mock_cls:
            mock_client = _mock_anthropic_client()
            mock_cls.return_value = mock_client
            mock_client.messages.create = AsyncMock(side_effect=Exception("auth error"))

            adapter = ClaudeAdapter(api_key="test-key")
            result = await adapter.health_check()

        assert result is False
