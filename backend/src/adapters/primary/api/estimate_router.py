from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....application.commands.estimate_task_command import EstimateTaskCommand
from ....application.use_cases.estimate_task_use_case import EstimateTaskUseCase
from ....domain.entities.task import Task, TaskType, TaskStatus, TaskPriority
from ....domain.services.estimation_service import EstimationService
from ....infrastructure.container import container

router = APIRouter(prefix="/api/v1/estimate", tags=["estimation"])


# ── Request / Response schemas ────────────────────────────────────────────────

class EstimateRequest(BaseModel):
    project_id: uuid.UUID
    title: str
    description: str
    acceptance_criteria: Optional[str] = None
    component_tags: list[str] = []


class PointsBreakdownResponse(BaseModel):
    frontend: int
    backend: int
    testing: int


class SimilarTaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    estimated: int
    actual: Optional[int]


class EstimationResponse(BaseModel):
    points: int
    confidence: float
    breakdown: PointsBreakdownResponse
    rationale: str
    similar_tasks: list[SimilarTaskResponse]
    risks: list[str]


class BreakdownEpicRequest(BaseModel):
    project_id: uuid.UUID
    epic_title: str
    description: str
    context: Optional[str] = None


class StoryItem(BaseModel):
    title: str
    description: str
    estimated_points: Optional[int] = None


class BreakdownEpicResponse(BaseModel):
    stories: list[StoryItem]


# ── Dependency providers ──────────────────────────────────────────────────────

def get_estimate_use_case() -> EstimateTaskUseCase:
    return EstimateTaskUseCase(
        llm=container.llm_router,
        embedding=container.embedding,
        vector_store=container.vector_store,
    )


def get_estimation_service() -> EstimationService:
    return EstimationService(llm=container.llm_router)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("", response_model=EstimationResponse)
async def estimate_task(
    body: EstimateRequest,
    use_case: Annotated[EstimateTaskUseCase, Depends(get_estimate_use_case)],
) -> EstimationResponse:
    command = EstimateTaskCommand(
        project_id=body.project_id,
        title=body.title,
        description=body.description,
        acceptance_criteria=body.acceptance_criteria,
        component_tags=body.component_tags,
    )
    try:
        result = await use_case.execute(command)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    est = result.estimation
    return EstimationResponse(
        points=est.points,
        confidence=est.confidence,
        breakdown=PointsBreakdownResponse(
            frontend=est.breakdown.frontend,
            backend=est.breakdown.backend,
            testing=est.breakdown.testing,
        ),
        rationale=est.rationale,
        similar_tasks=[
            SimilarTaskResponse(
                id=st.id,
                title=st.title,
                estimated=st.estimated_points,
                actual=st.actual_points,
            )
            for st in est.similar_tasks
        ],
        risks=est.risks,
    )


@router.post("/breakdown", response_model=BreakdownEpicResponse)
async def breakdown_epic(
    body: BreakdownEpicRequest,
    service: Annotated[EstimationService, Depends(get_estimation_service)],
) -> BreakdownEpicResponse:
    epic = Task(
        id=uuid.uuid4(),
        project_id=body.project_id,
        title=body.epic_title,
        description=body.description,
        type=TaskType.EPIC,
        status=TaskStatus.BACKLOG,
        priority=TaskPriority.MEDIUM,
    )
    try:
        stories = await service.breakdown_epic(epic)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return BreakdownEpicResponse(
        stories=[
            StoryItem(
                title=s.title,
                description=s.description,
                estimated_points=s.estimated_points,
            )
            for s in stories
        ]
    )
