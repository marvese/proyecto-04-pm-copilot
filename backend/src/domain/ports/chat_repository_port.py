from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from ..entities.chat import ChatMessage, ChatSession


class ChatRepositoryPort(ABC):
    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession: ...

    @abstractmethod
    async def get_session(self, session_id: uuid.UUID) -> ChatSession | None: ...

    @abstractmethod
    async def list_sessions(self, project_id: uuid.UUID | None = None) -> list[ChatSession]: ...

    @abstractmethod
    async def save_message(self, message: ChatMessage) -> ChatMessage: ...

    @abstractmethod
    async def get_message(self, message_id: uuid.UUID) -> ChatMessage | None: ...

    @abstractmethod
    async def get_session_for_message(self, message_id: uuid.UUID) -> ChatSession | None:
        """Returns the session owning this message (for project_id lookup)."""
        ...

    @abstractmethod
    async def list_messages(self, session_id: uuid.UUID) -> list[ChatMessage]: ...
