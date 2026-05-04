from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....domain.entities.project import Project, Sprint, SprintStatus
from ....domain.exceptions import DomainError
from ....domain.ports.project_repository_port import ProjectRepositoryPort
from ....domain.ports.sprint_repository_port import SprintRepositoryPort
from .models import ProjectORM, SprintORM


class PostgreSQLProjectAdapter(ProjectRepositoryPort):
    """Implements ProjectRepositoryPort using SQLAlchemy async + PostgreSQL."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    def _to_orm(self, project: Project) -> ProjectORM:
        return ProjectORM(
            id=project.id,
            name=project.name,
            description=project.description or None,
            jira_project_key=project.jira_project_key,
            confluence_space_key=project.confluence_space_key,
            github_repo=project.github_repo,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    def _to_entity(self, orm: ProjectORM) -> Project:
        return Project(
            id=orm.id,
            name=orm.name,
            description=orm.description or "",
            jira_project_key=orm.jira_project_key,
            confluence_space_key=orm.confluence_space_key,
            github_repo=orm.github_repo,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        async with self._session_factory() as session:
            result = await session.get(ProjectORM, project_id)
            return self._to_entity(result) if result else None

    async def list_all(self) -> list[Project]:
        async with self._session_factory() as session:
            stmt = select(ProjectORM).order_by(ProjectORM.created_at.desc())
            rows = await session.execute(stmt)
            return [self._to_entity(row) for row in rows.scalars().all()]

    async def save(self, project: Project) -> Project:
        async with self._session_factory() as session:
            async with session.begin():
                orm = self._to_orm(project)
                merged = await session.merge(orm)
                await session.flush()
                return self._to_entity(merged)

    async def delete(self, project_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                orm = await session.get(ProjectORM, project_id)
                if orm is not None:
                    await session.delete(orm)


class PostgreSQLSprintAdapter(SprintRepositoryPort):
    """Implements SprintRepositoryPort using SQLAlchemy async + PostgreSQL."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    def _to_orm(self, sprint: Sprint) -> SprintORM:
        return SprintORM(
            id=sprint.id,
            project_id=sprint.project_id,
            name=sprint.name,
            goal=sprint.goal,
            status=sprint.status.value,
            capacity_points=sprint.capacity_points,
            start_date=sprint.start_date,
            end_date=sprint.end_date,
            created_at=sprint.created_at,
        )

    def _to_entity(self, orm: SprintORM) -> Sprint:
        return Sprint(
            id=orm.id,
            project_id=orm.project_id,
            name=orm.name,
            goal=orm.goal,
            status=SprintStatus(orm.status),
            capacity_points=orm.capacity_points,
            start_date=orm.start_date,
            end_date=orm.end_date,
            created_at=orm.created_at,
        )

    async def get_by_id(self, sprint_id: uuid.UUID) -> Optional[Sprint]:
        async with self._session_factory() as session:
            result = await session.get(SprintORM, sprint_id)
            return self._to_entity(result) if result else None

    async def get_active(self, project_id: uuid.UUID) -> Optional[Sprint]:
        async with self._session_factory() as session:
            stmt = select(SprintORM).where(
                SprintORM.project_id == project_id,
                SprintORM.status == SprintStatus.ACTIVE.value,
            )
            result = await session.execute(stmt)
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None

    async def list_by_project(self, project_id: uuid.UUID) -> list[Sprint]:
        async with self._session_factory() as session:
            stmt = select(SprintORM).where(SprintORM.project_id == project_id)
            rows = await session.execute(stmt)
            return [self._to_entity(row) for row in rows.scalars().all()]

    async def save(self, sprint: Sprint) -> Sprint:
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    orm = self._to_orm(sprint)
                    merged = await session.merge(orm)
                    await session.flush()
                    return self._to_entity(merged)
        except IntegrityError as exc:
            raise DomainError(
                f"Project {sprint.project_id} already has an active sprint."
            ) from exc
