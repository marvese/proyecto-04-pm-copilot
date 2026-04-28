from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from ..entities.project import Sprint, SprintStatus


class SprintRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, sprint_id: uuid.UUID) -> Optional[Sprint]:
        ...

    @abstractmethod
    async def get_active(self, project_id: uuid.UUID) -> Optional[Sprint]:
        ...

    @abstractmethod
    async def list_by_project(self, project_id: uuid.UUID) -> list[Sprint]:
        ...

    @abstractmethod
    async def save(self, sprint: Sprint) -> Sprint:
        ...
