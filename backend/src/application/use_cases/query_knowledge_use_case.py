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
        similar = await self._rag.search(
            query=command.query,
            project_id=str(command.project_id),
            top_k=command.top_k,
        )
        if not similar:
            return KnowledgeQueryResult(
                answer="No se encontró información relevante en la base de conocimiento.",
                sources=[],
            )

        context_text = "\n\n".join(
            f"Fuente: {r.metadata.get('url', r.metadata.get('document_id', ''))}\n{r.content}"
            for r in similar
        )
        prompt = (
            f"Contexto del proyecto:\n{context_text}\n\n"
            f"Pregunta: {command.query}\n\n"
            "Responde basándote solo en el contexto proporcionado. "
            "Si la información no está en el contexto, indícalo."
        )
        response = await self._llm.complete(
            LLMRequest(
                prompt=prompt,
                task_type=LLMTaskType.SIMPLE_QA,
                max_tokens=1024,
                temperature=0.3,
            )
        )
        return KnowledgeQueryResult(answer=response.content, sources=similar)
