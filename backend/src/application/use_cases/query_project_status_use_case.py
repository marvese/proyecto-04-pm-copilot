from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from ...domain.entities.task import TaskStatus, TaskPriority
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
    """Returns aggregated status metrics for a project.

    Blocked tasks = IN_REVIEW with priority HIGH or CRITICAL.
    Persistence-agnostic: depends only on repository ports.
    """

    def __init__(
        self,
        task_repo: TaskRepositoryPort,
        sprint_repo: SprintRepositoryPort,
    ) -> None:
        self._task_repo = task_repo
        self._sprint_repo = sprint_repo

    async def execute(self, project_id: uuid.UUID) -> ProjectStatusResult:
        active_sprint = await self._sprint_repo.get_active(project_id)
        tasks = await self._task_repo.list_by_project(project_id)

        _blocked_priorities = {TaskPriority.HIGH, TaskPriority.CRITICAL}

        completed_points = sum(
            t.estimated_points or 0
            for t in tasks
            if t.status == TaskStatus.DONE
        )
        remaining_points = sum(
            t.estimated_points or 0
            for t in tasks
            if t.status != TaskStatus.DONE
        )
        total_points = completed_points + remaining_points

        blocked_task_count = sum(
            1 for t in tasks
            if t.status == TaskStatus.IN_REVIEW and t.priority in _blocked_priorities
        )

        days_remaining: Optional[int] = None
        if active_sprint and active_sprint.end_date:
            now = datetime.now(timezone.utc)
            end = active_sprint.end_date
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            days_remaining = max(0, (end - now).days)

        return ProjectStatusResult(
            active_sprint_name=active_sprint.name if active_sprint else None,
            completed_points=completed_points,
            remaining_points=remaining_points,
            total_points=total_points,
            days_remaining=days_remaining,
            blocked_task_count=blocked_task_count,
        )
