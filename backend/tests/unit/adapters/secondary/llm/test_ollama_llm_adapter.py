from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.adapters.secondary.llm.ollama_llm_adapter import OllamaLLMAdapter
from src.domain.ports.llm_port import LLMRequest, LLMTaskType


def make_request(prompt: str = "hello", system: str | None = None) -> LLMRequest:
    return LLMRequest(
        prompt=prompt,
        task_type=LLMTaskType.SIMPLE_QA,
        system=system,
        max_tokens=256,
        temperature=0.5,
    )


def _mock_httpx_client(response_json: dict):
    resp = MagicMock()
    resp.json.return_value = response_json
    resp.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=resp)
    return mock_client


class TestComplete:
    async def test_returns_llm_response(self) -> None:
        adapter = OllamaLLMAdapter()
        payload = {
            "message": {"content": "The answer is 42"},
            "model": "llama3.2",
            "prompt_eval_count": 10,
            "eval_count": 5,
        }
        with patch("httpx.AsyncClient", return_value=_mock_httpx_client(payload)):
            result = await adapter.complete(make_request())
        assert result.content == "The answer is 42"
        assert result.provider == "ollama"
        assert result.input_tokens == 10
        assert result.output_tokens == 5

    async def test_posts_to_correct_endpoint(self) -> None:
        adapter = OllamaLLMAdapter(base_url="http://ollama:11434", model="mistral")
        payload = {"message": {"content": "ok"}, "model": "mistral",
                   "prompt_eval_count": 1, "eval_count": 1}
        mock_client = _mock_httpx_client(payload)
        with patch("httpx.AsyncClient", return_value=mock_client):
            await adapter.complete(make_request())
        url = mock_client.post.call_args[0][0]
        assert url == "http://ollama:11434/api/chat"
        assert mock_client.post.call_args[1]["json"]["stream"] is False

    async def test_system_prompt_inserted_as_first_message(self) -> None:
        adapter = OllamaLLMAdapter()
        payload = {"message": {"content": "ok"}, "model": "llama3.2",
                   "prompt_eval_count": 1, "eval_count": 1}
        mock_client = _mock_httpx_client(payload)
        with patch("httpx.AsyncClient", return_value=mock_client):
            await adapter.complete(make_request(system="Be concise."))
        messages = mock_client.post.call_args[1]["json"]["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Be concise."
        assert messages[1]["role"] == "user"

    async def test_no_system_when_none(self) -> None:
        adapter = OllamaLLMAdapter()
        payload = {"message": {"content": "ok"}, "model": "llama3.2",
                   "prompt_eval_count": 1, "eval_count": 1}
        mock_client = _mock_httpx_client(payload)
        with patch("httpx.AsyncClient", return_value=mock_client):
            await adapter.complete(make_request(system=None))
        messages = mock_client.post.call_args[1]["json"]["messages"]
        assert all(m["role"] != "system" for m in messages)


class TestStream:
    async def test_yields_tokens(self) -> None:
        adapter = OllamaLLMAdapter()
        lines = [
            '{"message": {"content": "Hello"}, "done": false}',
            '{"message": {"content": " World"}, "done": false}',
            '{"message": {"content": ""}, "done": true}',
        ]

        async def fake_aiter_lines():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_lines = fake_aiter_lines

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        with patch("httpx.AsyncClient", return_value=mock_client):
            tokens = [t async for t in adapter.stream(make_request())]

        assert tokens == ["Hello", " World"]

    async def test_stream_stops_at_done(self) -> None:
        adapter = OllamaLLMAdapter()
        lines = [
            '{"message": {"content": "A"}, "done": false}',
            '{"message": {"content": ""}, "done": true}',
            '{"message": {"content": "B"}, "done": false}',  # should not be yielded
        ]

        async def fake_aiter_lines():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_lines = fake_aiter_lines

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        with patch("httpx.AsyncClient", return_value=mock_client):
            tokens = [t async for t in adapter.stream(make_request())]

        assert "B" not in tokens


class TestHealthCheck:
    async def test_returns_true_on_200(self) -> None:
        adapter = OllamaLLMAdapter()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)
        with patch("httpx.AsyncClient", return_value=mock_client):
            assert await adapter.health_check() is True

    async def test_returns_false_on_error(self) -> None:
        adapter = OllamaLLMAdapter()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        with patch("httpx.AsyncClient", return_value=mock_client):
            assert await adapter.health_check() is False
