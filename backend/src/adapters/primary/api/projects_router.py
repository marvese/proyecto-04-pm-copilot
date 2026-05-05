from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....application.use_cases.query_project_status_use_case import (
    QueryProjectStatusUseCase,
    ProjectStatusResult,
)
from ....infrastructure.container import container

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    jira_project_key: Optional[str]
    confluence_space_key: Optional[str]
    github_repo: Optional[str]


class CreateProjectRequest(BaseModel):
    name: str
    description: str
    jira_project_key: Optional[str] = None
    confluence_space_key: Optional[str] = None
    github_repo: Optional[str] = None


class ProjectStatusResponse(BaseModel):
    active_sprint_name: Optional[str]
    completed_points: int
    remaining_points: int
    total_points: int
    days_remaining: Optional[int]
    blocked_task_count: int


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_query_status_use_case() -> QueryProjectStatusUseCase:
    return container.query_project_status_use_case


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ProjectResponse])
async def list_projects() -> list[ProjectResponse]:
    # TODO: implement — PMCP-48
    raise NotImplementedError


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(body: CreateProjectRequest) -> ProjectResponse:
    # TODO: implement — PMCP-48
    raise NotImplementedError


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID) -> ProjectResponse:
    # TODO: implement — PMCP-48
    raise NotImplementedError


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(
    project_id: uuid.UUID,
    use_case: Annotated[QueryProjectStatusUseCase, Depends(get_query_status_use_case)],
) -> ProjectStatusResponse:
    project = await container.project_repo.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    result: ProjectStatusResult = await use_case.execute(project_id)

    return ProjectStatusResponse(
        active_sprint_name=result.active_sprint_name,
        completed_points=result.completed_points,
        remaining_points=result.remaining_points,
        total_points=result.total_points,
        days_remaining=result.days_remaining,
        blocked_task_count=result.blocked_task_count,
    )
