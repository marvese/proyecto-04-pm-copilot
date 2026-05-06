from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from ....application.commands.create_task_command import CreateTaskCommand
from ....application.use_cases.create_task_use_case import CreateTaskUseCase
from ....application.use_cases.sync_jira_use_case import SyncJiraUseCase
from ....application.commands.update_task_command import UpdateTaskCommand
from ....application.use_cases.update_task_use_case import UpdateTaskUseCase
from ....domain.entities.task import Task, TaskPriority, TaskStatus, TaskType, JiraSyncStatus
from ....domain.exceptions import DomainError
from ....domain.ports.task_repository_port import TaskRepositoryPort
from ....domain.ports.project_repository_port import ProjectRepositoryPort
from ....infrastructure.container import container

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


# ── Schemas ───────────────────────────────────────────────────────────────────

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


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_task_repo() -> TaskRepositoryPort:
    return container.task_repo


def get_project_repo() -> ProjectRepositoryPort:
    return container.project_repo


def get_create_task_use_case() -> CreateTaskUseCase:
    return container.create_task_use_case


def get_update_task_use_case() -> UpdateTaskUseCase:
    return container.update_task_use_case


def get_sync_jira_use_case() -> Optional[SyncJiraUseCase]:
    return container.sync_jira_use_case


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        type=task.type,
        status=task.status,
        priority=task.priority,
        estimated_points=task.estimated_points,
        actual_points=task.actual_points,
        sprint_id=task.sprint_id,
        jira_key=task.jira_key,
        jira_sync_status=task.jira_sync_status,
        tags=task.tags,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    project_id: uuid.UUID,
    repo: Annotated[TaskRepositoryPort, Depends(get_task_repo)],
    status: Optional[TaskStatus] = None,
    sprint_id: Optional[uuid.UUID] = None,
) -> list[TaskResponse]:
    tasks = await repo.list_by_project(project_id, status=status, sprint_id=sprint_id)
    return [_to_response(t) for t in tasks]


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    body: CreateTaskRequest,
    use_case: Annotated[CreateTaskUseCase, Depends(get_create_task_use_case)],
) -> TaskResponse:
    command = CreateTaskCommand(
        project_id=body.project_id,
        title=body.title,
        description=body.description,
        type=body.type,
        priority=body.priority,
        estimated_points=body.estimated_points,
        sprint_id=body.sprint_id,
        tags=body.tags,
    )
    task = await use_case.execute(command)
    return _to_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    repo: Annotated[TaskRepositoryPort, Depends(get_task_repo)],
) -> TaskResponse:
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_response(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_id: uuid.UUID,
    body: PatchTaskRequest,
    use_case: Annotated[UpdateTaskUseCase, Depends(get_update_task_use_case)],
) -> TaskResponse:
    updates = body.model_dump(exclude_unset=True)
    try:
        task = await use_case.execute(UpdateTaskCommand(task_id=task_id, updates=updates))
    except DomainError:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_response(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    repo: Annotated[TaskRepositoryPort, Depends(get_task_repo)],
) -> None:
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await repo.delete(task_id)


@router.post("/{task_id}/sync-jira", status_code=202)
async def sync_task_to_jira(
    task_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    repo: Annotated[TaskRepositoryPort, Depends(get_task_repo)],
    project_repo: Annotated[ProjectRepositoryPort, Depends(get_project_repo)],
    sync_use_case: Annotated[Optional[SyncJiraUseCase], Depends(get_sync_jira_use_case)],
) -> dict[str, str]:
    if sync_use_case is None:
        raise HTTPException(status_code=503, detail="Jira integration not configured")
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    project = await project_repo.get_by_id(task.project_id)
    if project is None or project.jira_project_key is None:
        raise HTTPException(status_code=422, detail="Project has no Jira project key configured")
    jira_project_key = project.jira_project_key
    background_tasks.add_task(sync_use_case.sync_single, task_id, jira_project_key)
    return {"status": "queued"}
