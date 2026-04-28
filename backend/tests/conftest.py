from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.domain.entities.task import Task, TaskType, TaskStatus, TaskPriority, JiraSyncStatus
from src.domain.entities.project import Project, Sprint, SprintStatus
from src.domain.ports.llm_port import LLMPort, LLMResponse, LLMTaskType
from src.domain.ports.task_repository_port import TaskRepositoryPort
from src.domain.ports.vector_store_port import VectorStorePort
from src.domain.ports.embedding_port import EmbeddingPort


@pytest.fixture
def project_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def task_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def sample_task(project_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    return Task(
        id=task_id,
        project_id=project_id,
        title="Implement estimation endpoint",
        description="Create POST /api/v1/estimate with RAG context",
        type=TaskType.STORY,
        status=TaskStatus.BACKLOG,
        priority=TaskPriority.HIGH,
        estimated_points=5,
        tags=["backend", "llm"],
    )


@pytest.fixture
def mock_llm() -> AsyncMock:
    mock = AsyncMock(spec=LLMPort)
    mock.complete.return_value = LLMResponse(
        content='{"points": 5, "confidence": 0.8, "breakdown": {"frontend": 1, "backend": 3, "testing": 1}, "rationale": "Similar to auth endpoint", "similar_tasks": [], "risks": []}',
        model="test-model",
        provider="mock",
        input_tokens=100,
        output_tokens=50,
    )
    return mock


@pytest.fixture
def mock_task_repo() -> AsyncMock:
    return AsyncMock(spec=TaskRepositoryPort)


@pytest.fixture
def mock_vector_store() -> AsyncMock:
    return AsyncMock(spec=VectorStorePort)


@pytest.fixture
def mock_embedding() -> AsyncMock:
    mock = AsyncMock(spec=EmbeddingPort)
    mock.embed.return_value = [0.1] * 768
    mock.embed_batch.return_value = [[0.1] * 768]
    mock.dimension = 768
    return mock
