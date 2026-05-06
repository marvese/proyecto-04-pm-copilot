from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ....domain.entities.user import User
from ....domain.ports.user_repository_port import UserRepositoryPort
from .models import UserORM


class PostgreSQLUserAdapter(UserRepositoryPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    def _to_entity(self, orm: UserORM) -> User:
        return User(
            id=orm.id,
            email=orm.email,
            hashed_password=orm.hashed_password,
            role=orm.role,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def _to_orm(self, user: User) -> UserORM:
        return UserORM(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self._session_factory() as session:
            stmt = select(UserORM).where(UserORM.email == email)
            result = await session.execute(stmt)
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        async with self._session_factory() as session:
            orm = await session.get(UserORM, user_id)
            return self._to_entity(orm) if orm else None

    async def save(self, user: User) -> User:
        async with self._session_factory() as session:
            async with session.begin():
                orm = self._to_orm(user)
                merged = await session.merge(orm)
                await session.flush()
                return self._to_entity(merged)
