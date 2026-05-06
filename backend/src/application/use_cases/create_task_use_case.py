from __future__ import annotations

import uuid

from ...domain.entities.task import Task, TaskStatus, JiraSyncStatus
from ...domain.ports.task_repository_port import TaskRepositoryPort
from ..commands.create_task_command import CreateTaskCommand


class CreateTaskUseCase:
    def __init__(self, task_repo: TaskRepositoryPort) -> None:
        self._task_repo = task_repo

    async def execute(self, command: CreateTaskCommand) -> Task:
        task = Task(
            id=uuid.uuid4(),
            project_id=command.project_id,
            title=command.title,
            description=command.description,
            type=command.type,
            status=TaskStatus.BACKLOG,
            priority=command.priority,
            estimated_points=command.estimated_points,
            sprint_id=command.sprint_id,
            tags=command.tags,
            jira_sync_status=JiraSyncStatus.LOCAL_ONLY,
        )
        return await self._task_repo.save(task)
