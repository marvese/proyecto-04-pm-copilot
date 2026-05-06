from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.adapters.primary.api.tasks_router import (
    get_task_repo,
    get_project_repo,
    get_create_task_use_case,
    get_update_task_use_case,
    get_sync_jira_use_case,
)
from src.application.use_cases.create_task_use_case import CreateTaskUseCase
from src.application.commands.update_task_command import UpdateTaskCommand
from src.application.use_cases.update_task_use_case import UpdateTaskUseCase
from src.application.use_cases.sync_jira_use_case import SyncJiraUseCase
from src.domain.entities.project import Project
from src.domain.entities.task import Task, TaskType, TaskStatus, TaskPriority, JiraSyncStatus
from src.domain.exceptions import DomainError
from src.domain.ports.task_repository_port import TaskRepositoryPort
from src.domain.ports.project_repository_port import ProjectRepositoryPort
from src.infrastructure.main import app

PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
TASK_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")
SPRINT_ID = uuid.UUID("00000000-0000-0000-0000-000000000030")


def _make_task(**overrides) -> Task:
    defaults = dict(
        id=TASK_ID,
        project_id=PROJECT_ID,
        title="Sample task",
        description="desc",
        type=TaskType.TASK,
        status=TaskStatus.BACKLOG,
        priority=TaskPriority.MEDIUM,
        estimated_points=3,
        actual_points=None,
        sprint_id=None,
        jira_key=None,
        jira_sync_status=JiraSyncStatus.LOCAL_ONLY,
        tags=["backend"],
    )
    return Task(**{**defaults, **overrides})


def _make_project(jira_key: str | None = "PMCP") -> Project:
    return Project(
        id=PROJECT_ID,
        name="Test project",
        description="desc",
        jira_project_key=jira_key,
        confluence_space_key=None,
        github_repo=None,
    )


def _mock_task_repo(*, get_by_id=None, list_return=None) -> TaskRepositoryPort:
    repo = AsyncMock(spec=TaskRepositoryPort)
    repo.get_by_id.return_value = get_by_id
    repo.list_by_project.return_value = list_return or []
    repo.save.side_effect = lambda t: t
    repo.delete.return_value = None
    return repo


def _mock_project_repo(project: Project | None = None) -> ProjectRepositoryPort:
    repo = AsyncMock(spec=ProjectRepositoryPort)
    repo.get_by_id.return_value = project
    return repo


def _mock_create_uc(task: Task) -> CreateTaskUseCase:
    uc = AsyncMock(spec=CreateTaskUseCase)
    uc.execute.return_value = task
    return uc


def _mock_update_uc(task: Task | None = None, raises: Exception | None = None) -> UpdateTaskUseCase:
    uc = AsyncMock(spec=UpdateTaskUseCase)
    if raises:
        uc.execute.side_effect = raises
    else:
        uc.execute.return_value = task
    return uc


# ── GET /api/v1/tasks ─────────────────────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestListTasks:
    def test_returns_empty_list(self) -> None:
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo()
        client = TestClient(app)
        resp = client.get(f"/api/v1/tasks?project_id={PROJECT_ID}")
        app.dependency_overrides.pop(get_task_repo, None)

        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_tasks_for_project(self) -> None:
        task = _make_task()
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(list_return=[task])
        client = TestClient(app)
        resp = client.get(f"/api/v1/tasks?project_id={PROJECT_ID}")
        app.dependency_overrides.pop(get_task_repo, None)

        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "Sample task"

    def test_response_fields(self) -> None:
        task = _make_task()
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(list_return=[task])
        client = TestClient(app)
        resp = client.get(f"/api/v1/tasks?project_id={PROJECT_ID}")
        app.dependency_overrides.pop(get_task_repo, None)

        item = resp.json()[0]
        assert item["id"] == str(TASK_ID)
        assert item["project_id"] == str(PROJECT_ID)
        assert item["status"] == "backlog"
        assert item["jira_sync_status"] == "local_only"
        assert item["tags"] == ["backend"]


# ── POST /api/v1/tasks ────────────────────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestCreateTask:
    def test_returns_201(self) -> None:
        task = _make_task()
        app.dependency_overrides[get_create_task_use_case] = lambda: _mock_create_uc(task)
        client = TestClient(app)
        resp = client.post(
            "/api/v1/tasks",
            json={"project_id": str(PROJECT_ID), "title": "Sample task", "description": "desc"},
        )
        app.dependency_overrides.pop(get_create_task_use_case, None)

        assert resp.status_code == 201
        assert resp.json()["title"] == "Sample task"

    def test_missing_title_returns_422(self) -> None:
        app.dependency_overrides[get_create_task_use_case] = lambda: _mock_create_uc(_make_task())
        client = TestClient(app)
        resp = client.post(
            "/api/v1/tasks",
            json={"project_id": str(PROJECT_ID), "description": "desc"},
        )
        app.dependency_overrides.pop(get_create_task_use_case, None)

        assert resp.status_code == 422


# ── GET /api/v1/tasks/{task_id} ───────────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestGetTask:
    def test_returns_task(self) -> None:
        task = _make_task()
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=task)
        client = TestClient(app)
        resp = client.get(f"/api/v1/tasks/{TASK_ID}")
        app.dependency_overrides.pop(get_task_repo, None)

        assert resp.status_code == 200
        assert resp.json()["id"] == str(TASK_ID)

    def test_returns_404_when_not_found(self) -> None:
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=None)
        client = TestClient(app)
        resp = client.get(f"/api/v1/tasks/{TASK_ID}")
        app.dependency_overrides.pop(get_task_repo, None)

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Task not found"


# ── PATCH /api/v1/tasks/{task_id} ────────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestPatchTask:
    def test_returns_updated_task(self) -> None:
        updated = _make_task(status=TaskStatus.IN_PROGRESS)
        app.dependency_overrides[get_update_task_use_case] = lambda: _mock_update_uc(updated)
        client = TestClient(app)
        resp = client.patch(
            f"/api/v1/tasks/{TASK_ID}",
            json={"status": "in_progress"},
        )
        app.dependency_overrides.pop(get_update_task_use_case, None)

        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_returns_404_when_use_case_raises_domain_error(self) -> None:
        app.dependency_overrides[get_update_task_use_case] = lambda: _mock_update_uc(
            raises=DomainError("Task not found")
        )
        client = TestClient(app)
        resp = client.patch(f"/api/v1/tasks/{TASK_ID}", json={"status": "done"})
        app.dependency_overrides.pop(get_update_task_use_case, None)

        assert resp.status_code == 404


# ── DELETE /api/v1/tasks/{task_id} ───────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestDeleteTask:
    def test_returns_204(self) -> None:
        task = _make_task()
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=task)
        client = TestClient(app)
        resp = client.delete(f"/api/v1/tasks/{TASK_ID}")
        app.dependency_overrides.pop(get_task_repo, None)

        assert resp.status_code == 204

    def test_returns_404_when_not_found(self) -> None:
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=None)
        client = TestClient(app)
        resp = client.delete(f"/api/v1/tasks/{TASK_ID}")
        app.dependency_overrides.pop(get_task_repo, None)

        assert resp.status_code == 404


# ── POST /api/v1/tasks/{task_id}/sync-jira ───────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestSyncTaskToJira:
    def test_returns_202_when_configured(self) -> None:
        task = _make_task()
        project = _make_project(jira_key="PMCP")
        sync_uc = AsyncMock(spec=SyncJiraUseCase)
        sync_uc.sync_single.return_value = None
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=task)
        app.dependency_overrides[get_project_repo] = lambda: _mock_project_repo(project)
        app.dependency_overrides[get_sync_jira_use_case] = lambda: sync_uc
        client = TestClient(app)
        resp = client.post(f"/api/v1/tasks/{TASK_ID}/sync-jira")
        app.dependency_overrides.pop(get_task_repo, None)
        app.dependency_overrides.pop(get_project_repo, None)
        app.dependency_overrides.pop(get_sync_jira_use_case, None)

        assert resp.status_code == 202
        assert resp.json() == {"status": "queued"}

    def test_returns_503_when_jira_not_configured(self) -> None:
        task = _make_task()
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=task)
        app.dependency_overrides[get_project_repo] = lambda: _mock_project_repo(_make_project())
        app.dependency_overrides[get_sync_jira_use_case] = lambda: None
        client = TestClient(app)
        resp = client.post(f"/api/v1/tasks/{TASK_ID}/sync-jira")
        app.dependency_overrides.pop(get_task_repo, None)
        app.dependency_overrides.pop(get_project_repo, None)
        app.dependency_overrides.pop(get_sync_jira_use_case, None)

        assert resp.status_code == 503

    def test_returns_404_when_task_not_found(self) -> None:
        sync_uc = AsyncMock(spec=SyncJiraUseCase)
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=None)
        app.dependency_overrides[get_project_repo] = lambda: _mock_project_repo(_make_project())
        app.dependency_overrides[get_sync_jira_use_case] = lambda: sync_uc
        client = TestClient(app)
        resp = client.post(f"/api/v1/tasks/{TASK_ID}/sync-jira")
        app.dependency_overrides.pop(get_task_repo, None)
        app.dependency_overrides.pop(get_project_repo, None)
        app.dependency_overrides.pop(get_sync_jira_use_case, None)

        assert resp.status_code == 404

    def test_returns_422_when_project_has_no_jira_key(self) -> None:
        task = _make_task()
        project = _make_project(jira_key=None)
        sync_uc = AsyncMock(spec=SyncJiraUseCase)
        app.dependency_overrides[get_task_repo] = lambda: _mock_task_repo(get_by_id=task)
        app.dependency_overrides[get_project_repo] = lambda: _mock_project_repo(project)
        app.dependency_overrides[get_sync_jira_use_case] = lambda: sync_uc
        client = TestClient(app)
        resp = client.post(f"/api/v1/tasks/{TASK_ID}/sync-jira")
        app.dependency_overrides.pop(get_task_repo, None)
        app.dependency_overrides.pop(get_project_repo, None)
        app.dependency_overrides.pop(get_sync_jira_use_case, None)

        assert resp.status_code == 422
