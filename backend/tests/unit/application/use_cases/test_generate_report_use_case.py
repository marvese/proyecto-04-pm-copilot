from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.commands.generate_report_command import GenerateReportCommand
from src.application.use_cases.generate_report_use_case import GenerateReportUseCase
from src.domain.entities.project import Project, Sprint, SprintStatus
from src.domain.entities.report import ReportType
from src.domain.entities.task import Task, TaskPriority, TaskStatus, TaskType
from src.domain.ports.llm_port import LLMResponse, LLMTaskType

PROJECT_ID = uuid.uuid4()
SPRINT_ID = uuid.uuid4()


def _make_project() -> Project:
    return Project(
        id=PROJECT_ID, name="Test Project", description="d",
        jira_project_key=None, confluence_space_key=None, github_repo=None,
    )


def _make_sprint() -> Sprint:
    return Sprint(
        id=SPRINT_ID, project_id=PROJECT_ID, name="Sprint 1",
        goal=None, status=SprintStatus.ACTIVE, capacity_points=40,
    )


def _make_task(status: TaskStatus = TaskStatus.DONE, pts: int = 3) -> Task:
    return Task(
        id=uuid.uuid4(), project_id=PROJECT_ID, title="Task",
        description=None, type=TaskType.STORY, status=status,
        priority=TaskPriority.MEDIUM, estimated_points=pts, actual_points=pts,
        assignee_id=None, sprint_id=SPRINT_ID, tags=[], jira_key=None,
        jira_sync_status="pending",
    )


def _make_llm_response(content: str = "# Report\n\nContent") -> LLMResponse:
    return LLMResponse(content=content, model="test", provider="test", input_tokens=10, output_tokens=20)


def _build_use_case(*, llm_response=None, llm_raises=False):
    llm = AsyncMock()
    if llm_raises:
        llm.complete.side_effect = Exception("LLM failed")
    else:
        llm.complete.return_value = llm_response or _make_llm_response()

    task_repo = AsyncMock()
    task_repo.list_by_project.return_value = [
        _make_task(TaskStatus.DONE, 3),
        _make_task(TaskStatus.DONE, 5),
        _make_task(TaskStatus.IN_PROGRESS, 2),
    ]

    sprint_repo = AsyncMock()
    sprint_repo.get_active.return_value = _make_sprint()
    sprint_repo.get_by_id.return_value = _make_sprint()

    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = _make_project()

    return GenerateReportUseCase(
        llm_port=llm, task_repo=task_repo,
        sprint_repo=sprint_repo, project_repo=project_repo,
    )


class TestSprintReport:
    @pytest.mark.asyncio
    async def test_returns_report_with_llm_content(self) -> None:
        uc = _build_use_case(llm_response=_make_llm_response("# Sprint Report\n\nGreat sprint!"))
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.SPRINT_STATUS)
        report = await uc.execute(cmd)

        assert report.type == ReportType.SPRINT_STATUS
        assert report.content == "# Sprint Report\n\nGreat sprint!"
        assert report.project_id == PROJECT_ID
        assert report.sprint_id == SPRINT_ID

    @pytest.mark.asyncio
    async def test_uses_generation_long_task_type(self) -> None:
        uc = _build_use_case()
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.SPRINT_STATUS)
        await uc.execute(cmd)

        call_args = uc._llm.complete.call_args[0][0]
        assert call_args.task_type == LLMTaskType.GENERATION_LONG

    @pytest.mark.asyncio
    async def test_fallback_on_llm_failure(self) -> None:
        uc = _build_use_case(llm_raises=True)
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.SPRINT_STATUS)
        report = await uc.execute(cmd)

        assert report.type == ReportType.SPRINT_STATUS
        assert "## Resumen Ejecutivo" in report.content
        assert "## Métricas del Sprint" in report.content

    @pytest.mark.asyncio
    async def test_fallback_includes_metrics(self) -> None:
        uc = _build_use_case(llm_raises=True)
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.SPRINT_STATUS)
        report = await uc.execute(cmd)

        assert "2/3" in report.content  # 2 done out of 3 tasks
        assert "8" in report.content    # 3 + 5 completed points


class TestProjectStatusReport:
    @pytest.mark.asyncio
    async def test_returns_project_status_report(self) -> None:
        uc = _build_use_case(llm_response=_make_llm_response("# Status"))
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.PROJECT_STATUS)
        report = await uc.execute(cmd)

        assert report.type == ReportType.PROJECT_STATUS
        assert "Test Project" in report.title

    @pytest.mark.asyncio
    async def test_fallback_contains_required_sections(self) -> None:
        uc = _build_use_case(llm_raises=True)
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.PROJECT_STATUS)
        report = await uc.execute(cmd)

        for section in ["## Estado General", "## Métricas de Velocidad",
                        "## Distribución de Tareas", "## Riesgos Identificados"]:
            assert section in report.content


class TestMeetingNotesReport:
    @pytest.mark.asyncio
    async def test_returns_meeting_notes_report(self) -> None:
        uc = _build_use_case(llm_response=_make_llm_response("# Meeting"))
        cmd = GenerateReportCommand(
            project_id=PROJECT_ID,
            type=ReportType.MEETING_NOTES,
            raw_input="Discutimos el sprint. Se decidió usar PostgreSQL.",
        )
        report = await uc.execute(cmd)

        assert report.type == ReportType.MEETING_NOTES
        assert "Meeting" in report.content

    @pytest.mark.asyncio
    async def test_fallback_without_notes(self) -> None:
        uc = _build_use_case(llm_raises=True)
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.MEETING_NOTES)
        report = await uc.execute(cmd)

        assert "## Resumen de la Reunión" in report.content
        assert "## Acciones y Responsables" in report.content


class TestReportEntity:
    @pytest.mark.asyncio
    async def test_report_has_uuid(self) -> None:
        uc = _build_use_case()
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.SPRINT_STATUS)
        report = await uc.execute(cmd)

        assert isinstance(report.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_no_active_sprint_returns_none_sprint_id(self) -> None:
        uc = _build_use_case()
        uc._sprint_repo.get_active.return_value = None
        cmd = GenerateReportCommand(project_id=PROJECT_ID, type=ReportType.SPRINT_STATUS)
        report = await uc.execute(cmd)

        assert report.sprint_id is None
