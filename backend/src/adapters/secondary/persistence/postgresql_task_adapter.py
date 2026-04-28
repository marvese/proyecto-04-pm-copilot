from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.task import Task, TaskStatus
from ....domain.ports.task_repository_port import TaskRepositoryPort


class PostgreSQLTaskAdapter(TaskRepositoryPort):
    """Implements TaskRepositoryPort using SQLAlchemy + PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        # TODO: implement — SELECT * FROM tasks WHERE id = :task_id
        raise NotImplementedError

    async def list_by_project(
        self,
        project_id: uuid.UUID,
        status: Optional[TaskStatus] = None,
        sprint_id: Optional[uuid.UUID] = None,
    ) -> list[Task]:
        # TODO: implement — SELECT with optional WHERE clauses
        raise NotImplementedError

    async def save(self, task: Task) -> Task:
        # TODO: implement — INSERT ... ON CONFLICT DO UPDATE
        raise NotImplementedError

    async def delete(self, task_id: uuid.UUID) -> None:
        # TODO: implement — DELETE FROM tasks WHERE id = :task_id
        raise NotImplementedError

    async def list_pending_jira_sync(self, project_id: uuid.UUID) -> list[Task]:
        # TODO: implement — WHERE jira_sync_status = 'pending'
        raise NotImplementedError
