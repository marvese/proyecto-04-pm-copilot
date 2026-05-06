from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.adapters.primary.api.reports_router import get_generate_report_use_case
from src.application.use_cases.generate_report_use_case import GenerateReportUseCase
from src.domain.entities.report import Report, ReportType
from src.infrastructure.main import app

PROJECT_ID = uuid.uuid4()
SPRINT_ID = uuid.uuid4()


def _make_report(report_type: ReportType = ReportType.SPRINT_STATUS) -> Report:
    return Report(
        id=uuid.uuid4(),
        project_id=PROJECT_ID,
        type=report_type,
        title="Sprint Summary — Test",
        content="## Resumen Ejecutivo\nGood sprint.",
        sprint_id=SPRINT_ID,
    )


def _mock_uc(report: Report | None = None) -> GenerateReportUseCase:
    uc = AsyncMock(spec=GenerateReportUseCase)
    uc.execute.return_value = report or _make_report()
    return uc


@pytest.mark.usefixtures("bypass_auth")
class TestGenerateReport:
    def test_returns_200_with_report(self) -> None:
        app.dependency_overrides[get_generate_report_use_case] = lambda: _mock_uc()
        client = TestClient(app)
        resp = client.post(
            "/api/v1/reports/generate",
            json={"project_id": str(PROJECT_ID), "report_type": "sprint_status"},
        )
        app.dependency_overrides.pop(get_generate_report_use_case, None)

        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "sprint_status"
        assert "content" in data
        assert "title" in data

    def test_sprint_endpoint_delegates_to_use_case(self) -> None:
        app.dependency_overrides[get_generate_report_use_case] = lambda: _mock_uc()
        client = TestClient(app)
        resp = client.post(
            "/api/v1/reports/sprint",
            json={"project_id": str(PROJECT_ID)},
        )
        app.dependency_overrides.pop(get_generate_report_use_case, None)

        assert resp.status_code == 200

    def test_status_endpoint_delegates_to_use_case(self) -> None:
        report = _make_report(ReportType.PROJECT_STATUS)
        app.dependency_overrides[get_generate_report_use_case] = lambda: _mock_uc(report)
        client = TestClient(app)
        resp = client.post(
            "/api/v1/reports/status",
            json={"project_id": str(PROJECT_ID)},
        )
        app.dependency_overrides.pop(get_generate_report_use_case, None)

        assert resp.status_code == 200
        assert resp.json()["type"] == "project_status"

    def test_meeting_notes_endpoint_accepts_raw_notes(self) -> None:
        report = _make_report(ReportType.MEETING_NOTES)
        app.dependency_overrides[get_generate_report_use_case] = lambda: _mock_uc(report)
        client = TestClient(app)
        resp = client.post(
            "/api/v1/reports/meeting-notes",
            json={"project_id": str(PROJECT_ID), "raw_notes": "Nos reunimos y decidimos usar FastAPI."},
        )
        app.dependency_overrides.pop(get_generate_report_use_case, None)

        assert resp.status_code == 200
        assert resp.json()["type"] == "meeting_notes"

    def test_missing_project_id_returns_422(self) -> None:
        client = TestClient(app)
        resp = client.post("/api/v1/reports/generate", json={"report_type": "sprint_status"})
        assert resp.status_code == 422

    def test_invalid_report_type_returns_422(self) -> None:
        client = TestClient(app)
        resp = client.post(
            "/api/v1/reports/generate",
            json={"project_id": str(PROJECT_ID), "report_type": "invalid_type"},
        )
        assert resp.status_code == 422
