from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from ..entities.project import Project


class ProjectRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        ...

    @abstractmethod
    async def list_all(self) -> list[Project]:
        ...

    @abstractmethod
    async def save(self, project: Project) -> Project:
        ...

    @abstractmethod
    async def delete(self, project_id: uuid.UUID) -> None:
        ...
