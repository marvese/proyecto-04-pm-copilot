from __future__ import annotations

import uuid
from dataclasses import dataclass

from ...domain.ports.llm_port import LLMPort, LLMTaskType, LLMRequest
from ...domain.ports.vector_store_port import SearchResult
from ...domain.services.rag_service import RAGService


@dataclass
class KnowledgeQueryCommand:
    project_id: uuid.UUID
    query: str
    top_k: int = 5


@dataclass
class KnowledgeQueryResult:
    answer: str
    sources: list[SearchResult]


class QueryKnowledgeUseCase:
    def __init__(self, llm_port: LLMPort, rag_service: RAGService) -> None:
        self._llm = llm_port
        self._rag = rag_service

    async def execute(self, command: KnowledgeQueryCommand) -> KnowledgeQueryResult:
        # TODO: implement
        # 1. rag_service.search(query, project_id, top_k)
        # 2. Build prompt with retrieved chunks as context
        # 3. LLM completes with SIMPLE_QA task type
        # 4. Return answer + source chunks (with citations)
        raise NotImplementedError
