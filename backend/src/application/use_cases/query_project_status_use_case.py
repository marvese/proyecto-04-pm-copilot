from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from ...domain.ports.sprint_repository_port import SprintRepositoryPort
from ...domain.ports.task_repository_port import TaskRepositoryPort


@dataclass
class ProjectStatusResult:
    active_sprint_name: Optional[str]
    completed_points: int
    remaining_points: int
    total_points: int
    days_remaining: Optional[int]
    blocked_task_count: int


class QueryProjectStatusUseCase:
    def __init__(
        self,
        task_repo: TaskRepositoryPort,
        sprint_repo: SprintRepositoryPort,
    ) -> None:
        self._task_repo = task_repo
        self._sprint_repo = sprint_repo

    async def execute(self, project_id: uuid.UUID) -> ProjectStatusResult:
        # TODO: implement
        raise NotImplementedError
