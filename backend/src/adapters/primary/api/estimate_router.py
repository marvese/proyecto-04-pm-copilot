from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/estimate", tags=["estimation"])


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
    estimated_points: Optional[int]


class BreakdownEpicResponse(BaseModel):
    stories: list[StoryItem]


@router.post("", response_model=EstimationResponse)
async def estimate_task(body: EstimateRequest) -> EstimationResponse:
    # TODO: implement — calls EstimateTaskUseCase
    raise NotImplementedError


@router.post("/breakdown", response_model=BreakdownEpicResponse)
async def breakdown_epic(body: BreakdownEpicRequest) -> BreakdownEpicResponse:
    # TODO: implement — calls EstimationService.breakdown_epic()
    raise NotImplementedError
