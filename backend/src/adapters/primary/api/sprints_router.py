from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ....domain.entities.project import SprintStatus

router = APIRouter(prefix="/api/v1/sprints", tags=["sprints"])


class SprintResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    goal: Optional[str]
    status: SprintStatus
    capacity_points: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]


class CreateSprintRequest(BaseModel):
    project_id: uuid.UUID
    name: str
    goal: Optional[str] = None
    capacity_points: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class PatchSprintRequest(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    status: Optional[SprintStatus] = None
    capacity_points: Optional[int] = None


@router.get("", response_model=list[SprintResponse])
async def list_sprints(project_id: uuid.UUID) -> list[SprintResponse]:
    # TODO: implement
    raise NotImplementedError


@router.post("", response_model=SprintResponse, status_code=201)
async def create_sprint(body: CreateSprintRequest) -> SprintResponse:
    # TODO: implement
    raise NotImplementedError


@router.get("/active", response_model=Optional[SprintResponse])
async def get_active_sprint(project_id: uuid.UUID) -> Optional[SprintResponse]:
    # TODO: implement
    raise NotImplementedError


@router.patch("/{sprint_id}", response_model=SprintResponse)
async def patch_sprint(sprint_id: uuid.UUID, body: PatchSprintRequest) -> SprintResponse:
    # TODO: implement
    raise NotImplementedError
