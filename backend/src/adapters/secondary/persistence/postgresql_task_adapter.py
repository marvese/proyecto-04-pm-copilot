from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....domain.entities.task import (
    JiraSyncStatus,
    Task,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from ....domain.ports.task_repository_port import TaskRepositoryPort
from .models import TaskORM


class PostgreSQLTaskAdapter(TaskRepositoryPort):
    """Implements TaskRepositoryPort using SQLAlchemy async + PostgreSQL."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    # ── conversions ──────────────────────────────────────────────────────────

    def _to_orm(self, task: Task) -> TaskORM:
        return TaskORM(
            id=task.id,
            project_id=task.project_id,
            sprint_id=task.sprint_id,
            title=task.title,
            description=task.description or None,
            type=task.type.value,
            status=task.status.value,
            priority=task.priority.value,
            estimated_points=task.estimated_points,
            actual_points=task.actual_points,
            assignee_id=task.assignee_id,
            jira_key=task.jira_key,
            jira_sync_status=task.jira_sync_status.value,
            tags=task.tags,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def _to_entity(self, orm: TaskORM) -> Task:
        return Task(
            id=orm.id,
            project_id=orm.project_id,
            title=orm.title,
            description=orm.description or "",
            type=TaskType(orm.type),
            status=TaskStatus(orm.status),
            priority=TaskPriority(orm.priority),
            estimated_points=orm.estimated_points,
            actual_points=orm.actual_points,
            sprint_id=orm.sprint_id,
            assignee_id=orm.assignee_id,
            jira_key=orm.jira_key,
            jira_sync_status=JiraSyncStatus(orm.jira_sync_status),
            tags=list(orm.tags) if orm.tags else [],
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    # ── port implementation ──────────────────────────────────────────────────

    async def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        async with self._session_factory() as session:
            result = await session.get(TaskORM, task_id)
            return self._to_entity(result) if result else None

    async def list_by_project(
        self,
        project_id: uuid.UUID,
        status: Optional[TaskStatus] = None,
        sprint_id: Optional[uuid.UUID] = None,
    ) -> list[Task]:
        async with self._session_factory() as session:
            stmt = select(TaskORM).where(TaskORM.project_id == project_id)
            if status is not None:
                stmt = stmt.where(TaskORM.status == status.value)
            if sprint_id is not None:
                stmt = stmt.where(TaskORM.sprint_id == sprint_id)
            rows = await session.execute(stmt)
            return [self._to_entity(row) for row in rows.scalars().all()]

    async def save(self, task: Task) -> Task:
        async with self._session_factory() as session:
            async with session.begin():
                orm = self._to_orm(task)
                merged = await session.merge(orm)
                await session.flush()
                return self._to_entity(merged)

    async def delete(self, task_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                orm = await session.get(TaskORM, task_id)
                if orm is not None:
                    await session.delete(orm)

    async def list_pending_jira_sync(self, project_id: uuid.UUID) -> list[Task]:
        async with self._session_factory() as session:
            stmt = select(TaskORM).where(
                TaskORM.project_id == project_id,
                TaskORM.jira_sync_status == JiraSyncStatus.PENDING.value,
            )
            rows = await session.execute(stmt)
            return [self._to_entity(row) for row in rows.scalars().all()]
