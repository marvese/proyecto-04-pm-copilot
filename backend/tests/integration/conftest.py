from __future__ import annotations

import uuid
from datetime import datetime

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.entities.project import Project
from src.infrastructure.config.settings import settings


@pytest.fixture
async def session_factory():
    """Create a fresh engine + session_factory per test (function scope)."""
    engine = create_async_engine(settings.database_url, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_db(session_factory):
    """Truncate all tables before each integration test to ensure isolation."""
    async with session_factory() as session:
        await session.execute(text("TRUNCATE projects CASCADE"))
        await session.commit()
    yield


@pytest.fixture
async def saved_project(session_factory) -> Project:
    """Create and persist a test project."""
    from src.adapters.secondary.persistence.postgresql_project_adapter import PostgreSQLProjectAdapter
    adapter = PostgreSQLProjectAdapter(session_factory)
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Integration test project",
        jira_project_key=None,
        confluence_space_key=None,
        github_repo=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return await adapter.save(project)
