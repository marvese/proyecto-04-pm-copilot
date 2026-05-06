from __future__ import annotations

import uuid
from abc import ABC, abstractmethod


class AuthPort(ABC):
    @abstractmethod
    def create_access_token(self, user_id: uuid.UUID, email: str) -> str: ...

    @abstractmethod
    def create_refresh_token(self, user_id: uuid.UUID, email: str) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> dict: ...

    @abstractmethod
    def hash_password(self, plain: str) -> str: ...

    @abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool: ...
