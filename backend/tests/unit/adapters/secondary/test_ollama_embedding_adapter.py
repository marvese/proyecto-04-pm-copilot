from __future__ import annotations

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from src.adapters.secondary.embedding.ollama_embedding_adapter import (
    OllamaEmbeddingAdapter,
    NOMIC_EMBED_DIMENSION,
    NOMIC_EMBED_MODEL,
)


def _fake_response(embedding: list[float]) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"embedding": embedding}
    resp.raise_for_status = MagicMock()
    return resp


VALID_EMBEDDING = [0.1] * NOMIC_EMBED_DIMENSION


class TestEmbed:
    async def test_returns_embedding_on_success(self) -> None:
        adapter = OllamaEmbeddingAdapter()
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=_fake_response(VALID_EMBEDDING))
            mock_client_cls.return_value = mock_client

            result = await adapter.embed("hello world")

        assert result == VALID_EMBEDDING
        assert len(result) == NOMIC_EMBED_DIMENSION

    async def test_posts_to_correct_endpoint(self) -> None:
        adapter = OllamaEmbeddingAdapter(base_url="http://ollama:11434")
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=_fake_response(VALID_EMBEDDING))
            mock_client_cls.return_value = mock_client

            await adapter.embed("test")

        call_args = mock_client.post.call_args
        assert "http://ollama:11434/api/embeddings" in call_args[0]
        assert call_args[1]["json"]["model"] == NOMIC_EMBED_MODEL
        assert call_args[1]["json"]["prompt"] == "test"

    async def test_raises_on_wrong_dimension(self) -> None:
        adapter = OllamaEmbeddingAdapter()
        bad_embedding = [0.1] * 512  # wrong size
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=_fake_response(bad_embedding))
            mock_client_cls.return_value = mock_client

            with pytest.raises(ValueError, match="Expected embedding dimension"):
                await adapter.embed("text")

    async def test_strips_trailing_slash_from_base_url(self) -> None:
        adapter = OllamaEmbeddingAdapter(base_url="http://localhost:11434/")
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=_fake_response(VALID_EMBEDDING))
            mock_client_cls.return_value = mock_client

            await adapter.embed("text")

        url = mock_client.post.call_args[0][0]
        assert "//" not in url[7:]  # no double slash after protocol


class TestEmbedBatch:
    async def test_returns_all_embeddings(self) -> None:
        adapter = OllamaEmbeddingAdapter()
        call_count = 0

        async def mock_embed(text: str) -> list[float]:
            nonlocal call_count
            call_count += 1
            return VALID_EMBEDDING

        adapter.embed = mock_embed  # type: ignore[method-assign]
        results = await adapter.embed_batch(["a", "b", "c"])

        assert len(results) == 3
        assert call_count == 3
        assert all(r == VALID_EMBEDDING for r in results)

    async def test_empty_batch_returns_empty(self) -> None:
        adapter = OllamaEmbeddingAdapter()
        results = await adapter.embed_batch([])
        assert results == []


class TestDimension:
    def test_dimension_property(self) -> None:
        assert OllamaEmbeddingAdapter().dimension == NOMIC_EMBED_DIMENSION
