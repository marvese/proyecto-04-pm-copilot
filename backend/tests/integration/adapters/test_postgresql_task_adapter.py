from __future__ import annotations

import uuid
from datetime import datetime

import pytest

from src.adapters.secondary.persistence.postgresql_task_adapter import PostgreSQLTaskAdapter
from src.domain.entities.task import JiraSyncStatus, Task, TaskPriority, TaskStatus, TaskType


def _make_task(project_id: uuid.UUID, **kwargs) -> Task:
    return Task(
        id=uuid.uuid4(),
        project_id=project_id,
        title=kwargs.get("title", "Test task"),
        description="Description",
        type=TaskType.STORY,
        status=kwargs.get("status", TaskStatus.BACKLOG),
        priority=TaskPriority.HIGH,
        estimated_points=kwargs.get("estimated_points", 5),
        tags=kwargs.get("tags", []),
        jira_sync_status=kwargs.get("jira_sync_status", JiraSyncStatus.LOCAL_ONLY),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.integration
class TestPostgreSQLTaskAdapter:
    @pytest.fixture
    def adapter(self, session_factory) -> PostgreSQLTaskAdapter:
        return PostgreSQLTaskAdapter(session_factory)

    async def test_save_and_retrieve_task(self, adapter, saved_project):
        task = _make_task(
            saved_project.id,
            title="Implement auth endpoint",
            tags=["backend", "api"],
            status=TaskStatus.BACKLOG,
        )

        await adapter.save(task)
        retrieved = await adapter.get_by_id(task.id)

        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.title == "Implement auth endpoint"
        assert retrieved.tags == ["backend", "api"]
        assert retrieved.status == TaskStatus.BACKLOG
        assert retrieved.type == TaskType.STORY
        assert retrieved.priority == TaskPriority.HIGH
        assert retrieved.estimated_points == 5

    async def test_get_by_id_returns_none_for_missing(self, adapter, saved_project):
        result = await adapter.get_by_id(uuid.uuid4())
        assert result is None

    async def test_list_pending_jira_sync(self, adapter, saved_project):
        pending1 = _make_task(saved_project.id, jira_sync_status=JiraSyncStatus.PENDING)
        pending2 = _make_task(saved_project.id, jira_sync_status=JiraSyncStatus.PENDING)
        synced = _make_task(saved_project.id, jira_sync_status=JiraSyncStatus.SYNCED)

        await adapter.save(pending1)
        await adapter.save(pending2)
        await adapter.save(synced)

        result = await adapter.list_pending_jira_sync(saved_project.id)

        assert len(result) == 2
        ids = {t.id for t in result}
        assert pending1.id in ids
        assert pending2.id in ids
        assert synced.id not in ids

    async def test_list_by_project_with_status_filter(self, adapter, saved_project):
        for _ in range(2):
            t = _make_task(saved_project.id, status=TaskStatus.DONE)
            t.actual_points = 3
            await adapter.save(t)
        for _ in range(2):
            await adapter.save(_make_task(saved_project.id, status=TaskStatus.IN_PROGRESS))

        done_tasks = await adapter.list_by_project(saved_project.id, status=TaskStatus.DONE)
        in_progress = await adapter.list_by_project(saved_project.id, status=TaskStatus.IN_PROGRESS)
        all_tasks = await adapter.list_by_project(saved_project.id)

        assert len(done_tasks) == 2
        assert len(in_progress) == 2
        assert len(all_tasks) == 4

    async def test_delete_task(self, adapter, saved_project):
        task = _make_task(saved_project.id)
        await adapter.save(task)

        assert await adapter.get_by_id(task.id) is not None

        await adapter.delete(task.id)

        assert await adapter.get_by_id(task.id) is None

    async def test_delete_nonexistent_is_noop(self, adapter, saved_project):
        await adapter.delete(uuid.uuid4())  # should not raise

    async def test_save_updates_existing_task(self, adapter, saved_project):
        task = _make_task(saved_project.id, status=TaskStatus.BACKLOG)
        await adapter.save(task)

        task.status = TaskStatus.IN_PROGRESS
        task.title = "Updated title"
        await adapter.save(task)

        retrieved = await adapter.get_by_id(task.id)
        assert retrieved is not None
        assert retrieved.status == TaskStatus.IN_PROGRESS
        assert retrieved.title == "Updated title"
