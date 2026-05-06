from __future__ import annotations

from datetime import datetime, timezone

from ...domain.entities.task import Task
from ...domain.exceptions import DomainError
from ...domain.ports.task_repository_port import TaskRepositoryPort
from ..commands.update_task_command import UpdateTaskCommand


class UpdateTaskUseCase:
    def __init__(self, task_repo: TaskRepositoryPort) -> None:
        self._task_repo = task_repo

    async def execute(self, command: UpdateTaskCommand) -> Task:
        task = await self._task_repo.get_by_id(command.task_id)
        if task is None:
            raise DomainError(f"Task {command.task_id} not found")
        for field, value in command.updates.items():
            if hasattr(task, field):
                setattr(task, field, value)
        task.updated_at = datetime.now(tz=timezone.utc)
        return await self._task_repo.save(task)
