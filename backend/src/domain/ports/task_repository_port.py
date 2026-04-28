from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from ..entities.task import Task, TaskStatus


class TaskRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: uuid.UUID,
        status: Optional[TaskStatus] = None,
        sprint_id: Optional[uuid.UUID] = None,
    ) -> list[Task]:
        ...

    @abstractmethod
    async def save(self, task: Task) -> Task:
        ...

    @abstractmethod
    async def delete(self, task_id: uuid.UUID) -> None:
        ...

    @abstractmethod
    async def list_pending_jira_sync(self, project_id: uuid.UUID) -> list[Task]:
        """Returns tasks with jira_sync_status=PENDING."""
        ...
