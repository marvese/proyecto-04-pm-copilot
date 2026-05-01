from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from src.domain.entities.knowledge import KnowledgeChunk, KnowledgeSource
from src.domain.ports.embedding_port import EmbeddingPort
from src.domain.ports.vector_store_port import VectorStorePort, SearchResult
from src.domain.services.rag_service import RAGService, KNOWLEDGE_COLLECTION

PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
FAKE_EMBEDDING = [0.1] * 768


def make_chunk(content: str = "test content") -> KnowledgeChunk:
    return KnowledgeChunk(
        id=uuid.uuid4(),
        project_id=PROJECT_ID,
        source=KnowledgeSource.CONFLUENCE,
        document_id="page-1",
        section="Intro",
        content=content,
        url="https://example.com/page-1",
    )


def make_service() -> tuple[RAGService, AsyncMock, AsyncMock]:
    embedding = AsyncMock(spec=EmbeddingPort)
    embedding.embed.return_value = FAKE_EMBEDDING
    vector_store = AsyncMock(spec=VectorStorePort)
    vector_store.search.return_value = []
    return RAGService(embedding, vector_store), embedding, vector_store


class TestIndexChunk:
    async def test_embeds_and_upserts(self) -> None:
        service, embedding, vector_store = make_service()
        chunk = make_chunk("hello world")

        await service.index_chunk(chunk)

        embedding.embed.assert_awaited_once_with("hello world")
        vector_store.upsert.assert_awaited_once()
        call_kwargs = vector_store.upsert.call_args.kwargs
        assert call_kwargs["id"] == str(chunk.id)
        assert call_kwargs["embedding"] == FAKE_EMBEDDING
        assert call_kwargs["content"] == "hello world"
        assert call_kwargs["collection"] == KNOWLEDGE_COLLECTION

    async def test_stores_embedding_on_chunk(self) -> None:
        service, _, _ = make_service()
        chunk = make_chunk()
        assert chunk.embedding is None
        await service.index_chunk(chunk)
        assert chunk.embedding == FAKE_EMBEDDING

    async def test_metadata_contains_project_id(self) -> None:
        service, _, vector_store = make_service()
        chunk = make_chunk()
        await service.index_chunk(chunk)
        metadata = vector_store.upsert.call_args.kwargs["metadata"]
        assert metadata["project_id"] == str(PROJECT_ID)
        assert metadata["source"] == KnowledgeSource.CONFLUENCE.value


class TestIndexChunks:
    async def test_indexes_all_chunks(self) -> None:
        service, embedding, vector_store = make_service()
        chunks = [make_chunk(f"content {i}") for i in range(3)]

        await service.index_chunks(chunks)

        assert embedding.embed.await_count == 3
        assert vector_store.upsert.await_count == 3


class TestSearch:
    async def test_embeds_query_and_searches(self) -> None:
        service, embedding, vector_store = make_service()
        fake_result = SearchResult(id="r1", content="found", score=0.9, metadata={})
        vector_store.search.return_value = [fake_result]

        results = await service.search("my query", str(PROJECT_ID), top_k=3)

        embedding.embed.assert_awaited_once_with("my query")
        vector_store.search.assert_awaited_once_with(
            query_embedding=FAKE_EMBEDDING,
            collection=KNOWLEDGE_COLLECTION,
            top_k=3,
            filter={"project_id": str(PROJECT_ID)},
        )
        assert len(results) == 1
        assert results[0].content == "found"

    async def test_returns_empty_when_no_results(self) -> None:
        service, _, _ = make_service()
        results = await service.search("query", str(PROJECT_ID))
        assert results == []
