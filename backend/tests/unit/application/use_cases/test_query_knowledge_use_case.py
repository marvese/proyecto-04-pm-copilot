from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.query_knowledge_use_case import (
    QueryKnowledgeUseCase,
    KnowledgeQueryCommand,
)
from src.domain.ports.llm_port import LLMPort, LLMResponse
from src.domain.ports.vector_store_port import SearchResult
from src.domain.services.rag_service import RAGService

PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def make_use_case(
    results: list[SearchResult], answer: str = "The answer."
) -> QueryKnowledgeUseCase:
    llm = AsyncMock(spec=LLMPort)
    llm.complete.return_value = LLMResponse(
        content=answer, model="test", provider="mock", input_tokens=10, output_tokens=5
    )
    rag = AsyncMock(spec=RAGService)
    rag.search.return_value = results
    return QueryKnowledgeUseCase(llm_port=llm, rag_service=rag)


def make_result(content: str = "doc content", score: float = 0.9) -> SearchResult:
    return SearchResult(
        id=str(uuid.uuid4()),
        content=content,
        score=score,
        metadata={"source": "confluence", "document_id": "page-1", "url": "http://x.com"},
    )


class TestQueryKnowledgeUseCase:
    async def test_returns_answer_with_sources(self) -> None:
        uc = make_use_case([make_result()], answer="42")
        cmd = KnowledgeQueryCommand(project_id=PROJECT_ID, query="What is the meaning?")
        result = await uc.execute(cmd)
        assert result.answer == "42"
        assert len(result.sources) == 1

    async def test_no_results_returns_fallback_message(self) -> None:
        uc = make_use_case([])
        cmd = KnowledgeQueryCommand(project_id=PROJECT_ID, query="unknown topic")
        result = await uc.execute(cmd)
        assert "No se encontró" in result.answer
        assert result.sources == []

    async def test_llm_not_called_when_no_results(self) -> None:
        llm = AsyncMock(spec=LLMPort)
        rag = AsyncMock(spec=RAGService)
        rag.search.return_value = []
        uc = QueryKnowledgeUseCase(llm_port=llm, rag_service=rag)
        cmd = KnowledgeQueryCommand(project_id=PROJECT_ID, query="x")
        await uc.execute(cmd)
        llm.complete.assert_not_awaited()

    async def test_context_included_in_prompt(self) -> None:
        llm = AsyncMock(spec=LLMPort)
        llm.complete.return_value = LLMResponse(
            content="ok", model="t", provider="m", input_tokens=1, output_tokens=1
        )
        rag = AsyncMock(spec=RAGService)
        rag.search.return_value = [make_result("important context")]
        uc = QueryKnowledgeUseCase(llm_port=llm, rag_service=rag)
        cmd = KnowledgeQueryCommand(project_id=PROJECT_ID, query="tell me")
        await uc.execute(cmd)

        prompt_used = llm.complete.call_args[0][0].prompt
        assert "important context" in prompt_used
        assert "tell me" in prompt_used

    async def test_search_called_with_project_id_and_top_k(self) -> None:
        uc = make_use_case([make_result()])
        cmd = KnowledgeQueryCommand(project_id=PROJECT_ID, query="q", top_k=7)
        await uc.execute(cmd)
        # Access rag mock via internal attribute
        uc._rag.search.assert_awaited_once_with(
            query="q", project_id=str(PROJECT_ID), top_k=7
        )
