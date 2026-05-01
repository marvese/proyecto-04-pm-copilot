from __future__ import annotations

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from ....domain.entities.knowledge import KnowledgeSource
from ....infrastructure.container import container
from ....application.use_cases.index_documents_use_case import IndexDocumentsCommand
from ....application.use_cases.query_knowledge_use_case import KnowledgeQueryCommand

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


class IndexRequest(BaseModel):
    project_id: uuid.UUID
    sources: list[KnowledgeSource]
    force_reindex: bool = False
    confluence_space_key: Optional[str] = None
    github_repo: Optional[str] = None
    jira_project_key: Optional[str] = None


class IndexStatusResponse(BaseModel):
    project_id: uuid.UUID
    status: str


class KnowledgeQueryRequest(BaseModel):
    project_id: uuid.UUID
    query: str
    top_k: int = 5


class SourceCitation(BaseModel):
    source: str
    document_id: str
    url: Optional[str]
    score: float


class KnowledgeQueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


async def _run_index(command: IndexDocumentsCommand) -> None:
    try:
        result = await container.index_documents_use_case.execute(command)
        logger.info(
            "Indexing complete: %d indexed, %d failed, sources=%s",
            result.indexed_count, result.failed_count,
            [s.value for s in result.sources_processed],
        )
    except Exception as exc:
        logger.error("Background indexing failed: %s", exc)


@router.post("/index", status_code=202)
async def trigger_index(body: IndexRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    command = IndexDocumentsCommand(
        project_id=body.project_id,
        sources=body.sources,
        force_reindex=body.force_reindex,
        confluence_space_key=body.confluence_space_key,
        github_repo=body.github_repo,
        jira_project_key=body.jira_project_key,
    )
    background_tasks.add_task(_run_index, command)
    return {"status": "accepted", "project_id": str(body.project_id)}


@router.get("/status", response_model=IndexStatusResponse)
async def index_status(project_id: uuid.UUID) -> IndexStatusResponse:
    # Placeholder until PMCP-27 (persistence) tracks index state
    return IndexStatusResponse(project_id=project_id, status="unknown")


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(body: KnowledgeQueryRequest) -> KnowledgeQueryResponse:
    command = KnowledgeQueryCommand(
        project_id=body.project_id,
        query=body.query,
        top_k=body.top_k,
    )
    try:
        result = await container.query_knowledge_use_case.execute(command)
    except Exception as exc:
        logger.error("query_knowledge error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return KnowledgeQueryResponse(
        answer=result.answer,
        sources=[
            SourceCitation(
                source=s.metadata.get("source", ""),
                document_id=s.metadata.get("document_id", s.id),
                url=s.metadata.get("url") or None,
                score=s.score,
            )
            for s in result.sources
        ],
    )
