from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.adapters.primary.api.projects_router import (
    get_project_repo,
    get_query_status_use_case,
)
from src.application.use_cases.query_project_status_use_case import (
    QueryProjectStatusUseCase,
    ProjectStatusResult,
)
from src.domain.entities.project import Project
from src.domain.ports.project_repository_port import ProjectRepositoryPort
from src.infrastructure.main import app

PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000042")
OTHER_ID = uuid.UUID("00000000-0000-0000-0000-000000000099")


def _make_project(project_id: uuid.UUID = PROJECT_ID, name: str = "Test Project") -> Project:
    return Project(
        id=project_id,
        name=name,
        description="desc",
        jira_project_key=None,
        confluence_space_key=None,
        github_repo=None,
    )


def _make_status_result(**overrides) -> ProjectStatusResult:
    defaults = dict(
        active_sprint_name="Sprint 1",
        completed_points=8,
        remaining_points=13,
        total_points=21,
        days_remaining=5,
        blocked_task_count=1,
    )
    return ProjectStatusResult(**{**defaults, **overrides})


def _mock_repo(
    *,
    get_by_id_return=None,
    list_all_return=None,
    save_side_effect=None,
) -> ProjectRepositoryPort:
    repo = AsyncMock(spec=ProjectRepositoryPort)
    repo.get_by_id.return_value = get_by_id_return
    repo.list_all.return_value = list_all_return or []
    if save_side_effect is not None:
        repo.save.side_effect = save_side_effect
    else:
        repo.save.return_value = get_by_id_return
    return repo


def _mock_use_case(result: ProjectStatusResult) -> QueryProjectStatusUseCase:
    uc = AsyncMock(spec=QueryProjectStatusUseCase)
    uc.execute.return_value = result
    return uc


# ── GET /api/v1/projects ──────────────────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestListProjects:
    def test_returns_empty_list(self) -> None:
        repo = _mock_repo(list_all_return=[])
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        resp = client.get("/api/v1/projects")
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_all_projects(self) -> None:
        projects = [
            _make_project(PROJECT_ID, "Alpha"),
            _make_project(OTHER_ID, "Beta"),
        ]
        repo = _mock_repo(list_all_return=projects)
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        resp = client.get("/api/v1/projects")
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["name"] == "Alpha"
        assert data[1]["name"] == "Beta"

    def test_response_fields(self) -> None:
        project = _make_project()
        repo = _mock_repo(list_all_return=[project])
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        resp = client.get("/api/v1/projects")
        app.dependency_overrides.clear()

        item = resp.json()[0]
        assert item["id"] == str(PROJECT_ID)
        assert item["name"] == "Test Project"
        assert item["description"] == "desc"
        assert item["jira_project_key"] is None
        assert item["confluence_space_key"] is None
        assert item["github_repo"] is None


# ── POST /api/v1/projects ─────────────────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestCreateProject:
    def test_returns_201_with_saved_project(self) -> None:
        saved = _make_project()
        repo = _mock_repo(save_side_effect=None)
        repo.save.return_value = saved
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        resp = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "desc"},
        )
        app.dependency_overrides.clear()

        assert resp.status_code == 201
        assert resp.json()["name"] == "Test Project"

    def test_passes_optional_fields_to_repo(self) -> None:
        captured: list[Project] = []

        async def capture_save(project: Project) -> Project:
            captured.append(project)
            return project

        repo = _mock_repo()
        repo.save.side_effect = capture_save
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        client.post(
            "/api/v1/projects",
            json={
                "name": "P",
                "description": "d",
                "jira_project_key": "PMCP",
                "confluence_space_key": "CS",
                "github_repo": "org/repo",
            },
        )
        app.dependency_overrides.clear()

        assert len(captured) == 1
        p = captured[0]
        assert p.jira_project_key == "PMCP"
        assert p.confluence_space_key == "CS"
        assert p.github_repo == "org/repo"

    def test_missing_name_returns_422(self) -> None:
        repo = _mock_repo()
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        resp = client.post("/api/v1/projects", json={"description": "d"})
        app.dependency_overrides.clear()

        assert resp.status_code == 422


# ── GET /api/v1/projects/{id} ─────────────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestGetProject:
    def test_returns_200_with_project(self) -> None:
        repo = _mock_repo(get_by_id_return=_make_project())
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        resp = client.get(f"/api/v1/projects/{PROJECT_ID}")
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json()["id"] == str(PROJECT_ID)

    def test_returns_404_when_not_found(self) -> None:
        repo = _mock_repo(get_by_id_return=None)
        app.dependency_overrides[get_project_repo] = lambda: repo
        client = TestClient(app)
        resp = client.get(f"/api/v1/projects/{PROJECT_ID}")
        app.dependency_overrides.clear()

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Project not found"


# ── GET /api/v1/projects/{id}/status ─────────────────────────────────────────

@pytest.mark.usefixtures("bypass_auth")
class TestGetProjectStatus:
    def test_returns_200_with_status_fields(self) -> None:
        result = _make_status_result()
        repo = _mock_repo(get_by_id_return=_make_project())
        app.dependency_overrides[get_project_repo] = lambda: repo
        app.dependency_overrides[get_query_status_use_case] = lambda: _mock_use_case(result)
        client = TestClient(app)
        resp = client.get(f"/api/v1/projects/{PROJECT_ID}/status")
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["active_sprint_name"] == "Sprint 1"
        assert data["completed_points"] == 8
        assert data["remaining_points"] == 13
        assert data["total_points"] == 21
        assert data["days_remaining"] == 5
        assert data["blocked_task_count"] == 1

    def test_returns_404_when_project_not_found(self) -> None:
        repo = _mock_repo(get_by_id_return=None)
        app.dependency_overrides[get_project_repo] = lambda: repo
        app.dependency_overrides[get_query_status_use_case] = lambda: AsyncMock(
            spec=QueryProjectStatusUseCase
        )
        client = TestClient(app)
        resp = client.get(f"/api/v1/projects/{PROJECT_ID}/status")
        app.dependency_overrides.clear()

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Project not found"

    def test_null_sprint_and_days_returned_as_none(self) -> None:
        result = _make_status_result(active_sprint_name=None, days_remaining=None)
        repo = _mock_repo(get_by_id_return=_make_project())
        app.dependency_overrides[get_project_repo] = lambda: repo
        app.dependency_overrides[get_query_status_use_case] = lambda: _mock_use_case(result)
        client = TestClient(app)
        resp = client.get(f"/api/v1/projects/{PROJECT_ID}/status")
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["active_sprint_name"] is None
        assert data["days_remaining"] is None
