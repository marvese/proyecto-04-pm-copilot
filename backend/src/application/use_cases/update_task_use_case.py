from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Optional

from ...domain.entities.task import Task
from ...domain.ports.task_repository_port import TaskRepositoryPort


@dataclass
class UpdateTaskCommand:
    task_id: uuid.UUID
    updates: dict[str, Any]


class UpdateTaskUseCase:
    def __init__(self, task_repo: TaskRepositoryPort) -> None:
        self._task_repo = task_repo

    async def execute(self, command: UpdateTaskCommand) -> Task:
        # TODO: implement
        # 1. Fetch task (raise 404 if not found)
        # 2. Apply updates to entity
        # 3. Persist and return updated task
        raise NotImplementedError
