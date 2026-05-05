from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.adapters.primary.api.projects_router import get_query_status_use_case
from src.application.use_cases.query_project_status_use_case import (
    QueryProjectStatusUseCase,
    ProjectStatusResult,
)
from src.domain.entities.project import Project
from src.infrastructure.main import app

PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000042")


def _make_project() -> Project:
    return Project(
        id=PROJECT_ID,
        name="Test Project",
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


def _mock_use_case(result: ProjectStatusResult) -> QueryProjectStatusUseCase:
    uc = AsyncMock(spec=QueryProjectStatusUseCase)
    uc.execute.return_value = result
    return uc


class TestGetProjectStatus:
    def test_returns_200_with_status_fields(self) -> None:
        result = _make_status_result()
        with (
            patch("src.adapters.primary.api.projects_router.container") as mock_container,
        ):
            mock_container.project_repo.get_by_id = AsyncMock(return_value=_make_project())
            mock_container.query_project_status_use_case = _mock_use_case(result)

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
        with (
            patch("src.adapters.primary.api.projects_router.container") as mock_container,
        ):
            mock_container.project_repo.get_by_id = AsyncMock(return_value=None)

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
        with (
            patch("src.adapters.primary.api.projects_router.container") as mock_container,
        ):
            mock_container.project_repo.get_by_id = AsyncMock(return_value=_make_project())
            mock_container.query_project_status_use_case = _mock_use_case(result)

            app.dependency_overrides[get_query_status_use_case] = lambda: _mock_use_case(result)
            client = TestClient(app)
            resp = client.get(f"/api/v1/projects/{PROJECT_ID}/status")
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["active_sprint_name"] is None
        assert data["days_remaining"] is None
