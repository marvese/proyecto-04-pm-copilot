from __future__ import annotations

import uuid
from datetime import datetime

import pytest

from src.adapters.secondary.persistence.postgresql_project_adapter import (
    PostgreSQLProjectAdapter,
    PostgreSQLSprintAdapter,
)
from src.domain.entities.project import Project, Sprint, SprintStatus
from src.domain.exceptions import DomainError


def _make_project(**kwargs) -> Project:
    return Project(
        id=uuid.uuid4(),
        name=kwargs.get("name", f"Project {uuid.uuid4().hex[:6]}"),
        description="Test description",
        jira_project_key=None,
        confluence_space_key=None,
        github_repo=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def _make_sprint(project_id: uuid.UUID, **kwargs) -> Sprint:
    return Sprint(
        id=uuid.uuid4(),
        project_id=project_id,
        name=kwargs.get("name", f"Sprint {uuid.uuid4().hex[:4]}"),
        goal=None,
        status=kwargs.get("status", SprintStatus.PLANNED),
        capacity_points=kwargs.get("capacity_points", None),
        created_at=datetime.utcnow(),
    )


@pytest.mark.integration
class TestPostgreSQLProjectAdapter:
    @pytest.fixture
    def adapter(self, session_factory) -> PostgreSQLProjectAdapter:
        return PostgreSQLProjectAdapter(session_factory)

    async def test_save_and_retrieve_project(self, adapter):
        project = _make_project(name="My Test Project")
        await adapter.save(project)

        retrieved = await adapter.get_by_id(project.id)

        assert retrieved is not None
        assert retrieved.id == project.id
        assert retrieved.name == "My Test Project"
        assert retrieved.description == "Test description"

    async def test_get_by_id_returns_none_for_missing(self, adapter):
        assert await adapter.get_by_id(uuid.uuid4()) is None

    async def test_list_all_ordered_by_created_at_desc(self, adapter):
        p1 = _make_project()
        p2 = _make_project()
        await adapter.save(p1)
        await adapter.save(p2)

        all_projects = await adapter.list_all()

        assert len(all_projects) >= 2
        # Verify ordering: most recently created first
        dates = [p.created_at for p in all_projects]
        assert dates == sorted(dates, reverse=True)

    async def test_delete_project(self, adapter):
        project = _make_project()
        await adapter.save(project)
        assert await adapter.get_by_id(project.id) is not None

        await adapter.delete(project.id)

        assert await adapter.get_by_id(project.id) is None

    async def test_delete_cascades_to_tasks(self, adapter, session_factory):
        from src.adapters.secondary.persistence.postgresql_task_adapter import PostgreSQLTaskAdapter
        from src.domain.entities.task import Task, TaskType, TaskStatus, TaskPriority, JiraSyncStatus

        project = _make_project()
        await adapter.save(project)

        task_adapter = PostgreSQLTaskAdapter(session_factory)
        task = Task(
            id=uuid.uuid4(),
            project_id=project.id,
            title="Cascaded task",
            description="",
            type=TaskType.TASK,
            status=TaskStatus.BACKLOG,
            priority=TaskPriority.LOW,
            tags=[],
            jira_sync_status=JiraSyncStatus.LOCAL_ONLY,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await task_adapter.save(task)

        await adapter.delete(project.id)

        assert await task_adapter.get_by_id(task.id) is None


@pytest.mark.integration
class TestPostgreSQLSprintAdapter:
    @pytest.fixture
    def adapter(self, session_factory) -> PostgreSQLSprintAdapter:
        return PostgreSQLSprintAdapter(session_factory)

    async def test_save_and_retrieve_sprint(self, adapter, saved_project):
        sprint = _make_sprint(saved_project.id, name="Sprint 1")
        await adapter.save(sprint)

        retrieved = await adapter.get_by_id(sprint.id)

        assert retrieved is not None
        assert retrieved.id == sprint.id
        assert retrieved.name == "Sprint 1"
        assert retrieved.status == SprintStatus.PLANNED

    async def test_get_active_returns_none_when_no_active_sprint(self, adapter, saved_project):
        sprint = _make_sprint(saved_project.id, status=SprintStatus.PLANNED)
        await adapter.save(sprint)

        result = await adapter.get_active(saved_project.id)

        assert result is None

    async def test_get_active_returns_active_sprint(self, adapter, saved_project):
        active = _make_sprint(saved_project.id, name="Active Sprint", status=SprintStatus.ACTIVE)
        planned = _make_sprint(saved_project.id, name="Planned Sprint", status=SprintStatus.PLANNED)
        await adapter.save(planned)
        await adapter.save(active)

        result = await adapter.get_active(saved_project.id)

        assert result is not None
        assert result.id == active.id
        assert result.status == SprintStatus.ACTIVE

    async def test_save_second_active_sprint_raises_domain_error(self, adapter, saved_project):
        first = _make_sprint(saved_project.id, status=SprintStatus.ACTIVE)
        second = _make_sprint(saved_project.id, status=SprintStatus.ACTIVE)

        await adapter.save(first)

        with pytest.raises(DomainError):
            await adapter.save(second)

    async def test_list_by_project(self, adapter, saved_project):
        for i in range(3):
            await adapter.save(_make_sprint(saved_project.id, name=f"Sprint {i}"))

        sprints = await adapter.list_by_project(saved_project.id)

        assert len(sprints) == 3

    async def test_get_by_id_returns_none_for_missing(self, adapter, saved_project):
        assert await adapter.get_by_id(uuid.uuid4()) is None
