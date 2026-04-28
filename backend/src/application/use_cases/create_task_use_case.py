from __future__ import annotations

import uuid

from ...domain.entities.task import Task, TaskStatus, JiraSyncStatus
from ...domain.ports.task_repository_port import TaskRepositoryPort
from ..commands.create_task_command import CreateTaskCommand


class CreateTaskUseCase:
    def __init__(self, task_repo: TaskRepositoryPort) -> None:
        self._task_repo = task_repo

    async def execute(self, command: CreateTaskCommand) -> Task:
        # TODO: implement
        # 1. Build Task entity from command
        # 2. Persist via task_repo.save()
        # 3. Return saved task
        raise NotImplementedError
