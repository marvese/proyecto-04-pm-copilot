from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....domain.entities.chat import ChatMessage, ChatSession
from ....domain.ports.chat_repository_port import ChatRepositoryPort
from .models import ChatMessageORM, ChatSessionORM


def _session_to_entity(row: ChatSessionORM) -> ChatSession:
    return ChatSession(
        id=row.id,
        project_id=row.project_id,
        created_at=row.created_at,
    )


def _message_to_entity(row: ChatMessageORM) -> ChatMessage:
    return ChatMessage(
        id=row.id,
        session_id=row.session_id,
        role=row.role,
        content=row.content,
        created_at=row.created_at,
    )


class PostgreSQLChatAdapter(ChatRepositoryPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session_factory

    async def create_session(self, session: ChatSession) -> ChatSession:
        async with self._factory() as db:
            row = ChatSessionORM(
                id=session.id,
                project_id=session.project_id,
                created_at=session.created_at,
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            return _session_to_entity(row)

    async def get_session(self, session_id: uuid.UUID) -> ChatSession | None:
        async with self._factory() as db:
            row = await db.get(ChatSessionORM, session_id)
            return _session_to_entity(row) if row else None

    async def list_sessions(self, project_id: uuid.UUID | None = None) -> list[ChatSession]:
        async with self._factory() as db:
            stmt = select(ChatSessionORM).order_by(ChatSessionORM.created_at.desc())
            if project_id:
                stmt = stmt.where(ChatSessionORM.project_id == project_id)
            result = await db.execute(stmt)
            return [_session_to_entity(r) for r in result.scalars()]

    async def save_message(self, message: ChatMessage) -> ChatMessage:
        async with self._factory() as db:
            row = ChatMessageORM(
                id=message.id,
                session_id=message.session_id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            return _message_to_entity(row)

    async def get_message(self, message_id: uuid.UUID) -> ChatMessage | None:
        async with self._factory() as db:
            row = await db.get(ChatMessageORM, message_id)
            return _message_to_entity(row) if row else None

    async def list_messages(self, session_id: uuid.UUID) -> list[ChatMessage]:
        async with self._factory() as db:
            stmt = (
                select(ChatMessageORM)
                .where(ChatMessageORM.session_id == session_id)
                .order_by(ChatMessageORM.created_at)
            )
            result = await db.execute(stmt)
            return [_message_to_entity(r) for r in result.scalars()]

    async def get_session_for_message(self, message_id: uuid.UUID) -> ChatSession | None:
        async with self._factory() as db:
            msg_row = await db.get(ChatMessageORM, message_id)
            if msg_row is None:
                return None
            session_row = await db.get(ChatSessionORM, msg_row.session_id)
            return _session_to_entity(session_row) if session_row else None
