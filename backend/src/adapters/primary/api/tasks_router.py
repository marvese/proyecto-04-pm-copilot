from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ....domain.entities.task import TaskType, TaskStatus, TaskPriority, JiraSyncStatus

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


class TaskResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str
    type: TaskType
    status: TaskStatus
    priority: TaskPriority
    estimated_points: Optional[int]
    actual_points: Optional[int]
    sprint_id: Optional[uuid.UUID]
    jira_key: Optional[str]
    jira_sync_status: JiraSyncStatus
    tags: list[str]


class CreateTaskRequest(BaseModel):
    project_id: uuid.UUID
    title: str
    description: str
    type: TaskType = TaskType.TASK
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_points: Optional[int] = None
    sprint_id: Optional[uuid.UUID] = None
    tags: list[str] = []


class PatchTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    estimated_points: Optional[int] = None
    actual_points: Optional[int] = None
    sprint_id: Optional[uuid.UUID] = None
    tags: Optional[list[str]] = None


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    project_id: uuid.UUID = Query(...),
    status: Optional[TaskStatus] = None,
    sprint_id: Optional[uuid.UUID] = None,
) -> list[TaskResponse]:
    # TODO: implement
    raise NotImplementedError


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(body: CreateTaskRequest) -> TaskResponse:
    # TODO: implement
    raise NotImplementedError


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID) -> TaskResponse:
    # TODO: implement
    raise NotImplementedError


@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(task_id: uuid.UUID, body: PatchTaskRequest) -> TaskResponse:
    # TODO: implement
    raise NotImplementedError


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: uuid.UUID) -> None:
    # TODO: implement
    raise NotImplementedError


@router.post("/{task_id}/sync-jira", status_code=202)
async def sync_task_to_jira(task_id: uuid.UUID) -> dict[str, str]:
    # TODO: implement — triggers immediate sync for this task
    raise NotImplementedError
