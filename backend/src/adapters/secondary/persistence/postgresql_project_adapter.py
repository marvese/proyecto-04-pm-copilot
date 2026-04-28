from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.project import Project, Sprint
from ....domain.ports.project_repository_port import ProjectRepositoryPort
from ....domain.ports.sprint_repository_port import SprintRepositoryPort


class PostgreSQLProjectAdapter(ProjectRepositoryPort):
    """Implements ProjectRepositoryPort using SQLAlchemy + PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        # TODO: implement
        raise NotImplementedError

    async def list_all(self) -> list[Project]:
        # TODO: implement
        raise NotImplementedError

    async def save(self, project: Project) -> Project:
        # TODO: implement
        raise NotImplementedError

    async def delete(self, project_id: uuid.UUID) -> None:
        # TODO: implement
        raise NotImplementedError


class PostgreSQLSprintAdapter(SprintRepositoryPort):
    """Implements SprintRepositoryPort using SQLAlchemy + PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, sprint_id: uuid.UUID) -> Optional[Sprint]:
        # TODO: implement
        raise NotImplementedError

    async def get_active(self, project_id: uuid.UUID) -> Optional[Sprint]:
        # TODO: implement — WHERE status = 'active' AND project_id = :project_id
        raise NotImplementedError

    async def list_by_project(self, project_id: uuid.UUID) -> list[Sprint]:
        # TODO: implement
        raise NotImplementedError

    async def save(self, sprint: Sprint) -> Sprint:
        # TODO: implement
        raise NotImplementedError
