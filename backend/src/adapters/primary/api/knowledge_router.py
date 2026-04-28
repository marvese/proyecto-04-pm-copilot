from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from ....domain.entities.knowledge import KnowledgeSource

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


class IndexRequest(BaseModel):
    project_id: uuid.UUID
    sources: list[KnowledgeSource]
    force_reindex: bool = False


class IndexStatusResponse(BaseModel):
    project_id: uuid.UUID
    last_indexed_at: Optional[str]
    chunk_count: int
    sources: list[KnowledgeSource]


class KnowledgeQueryRequest(BaseModel):
    project_id: uuid.UUID
    query: str
    top_k: int = 5


class SourceCitation(BaseModel):
    source: KnowledgeSource
    document_id: str
    url: Optional[str]
    score: float


class KnowledgeQueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


@router.post("/index", status_code=202)
async def trigger_index(body: IndexRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    # TODO: implement — triggers IndexDocumentsUseCase as background task
    raise NotImplementedError


@router.get("/status", response_model=IndexStatusResponse)
async def index_status(project_id: uuid.UUID) -> IndexStatusResponse:
    # TODO: implement
    raise NotImplementedError


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(body: KnowledgeQueryRequest) -> KnowledgeQueryResponse:
    # TODO: implement — calls QueryKnowledgeUseCase
    raise NotImplementedError
