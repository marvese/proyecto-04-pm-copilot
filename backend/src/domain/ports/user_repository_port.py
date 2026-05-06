from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from ..entities.user import User


class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...
