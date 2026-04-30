from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.query_project_status_use_case import (
    QueryProjectStatusUseCase,
    ProjectStatusResult,
)
from src.domain.entities.project import Sprint, SprintStatus
from src.domain.entities.task import Task, TaskStatus, TaskPriority, TaskType, JiraSyncStatus
from src.domain.ports.task_repository_port import TaskRepositoryPort
from src.domain.ports.sprint_repository_port import SprintRepositoryPort


# ────────────────────────── helpers ──────────────────────────

def make_task(
    project_id: uuid.UUID,
    status: TaskStatus = TaskStatus.BACKLOG,
    priority: TaskPriority = TaskPriority.MEDIUM,
    points: int = 3,
) -> Task:
    return Task(
        id=uuid.uuid4(),
        project_id=project_id,
        title="Task",
        description="",
        type=TaskType.STORY,
        status=status,
        priority=priority,
        estimated_points=points,
        tags=[],
        jira_sync_status=JiraSyncStatus.PENDING,
    )


def make_sprint(
    project_id: uuid.UUID,
    status: SprintStatus = SprintStatus.ACTIVE,
    name: str = "Sprint 1",
    end_date: datetime | None = None,
) -> Sprint:
    return Sprint(
        id=uuid.uuid4(),
        project_id=project_id,
        name=name,
        goal=None,
        status=status,
        capacity_points=40,
        end_date=end_date,
    )


def make_use_case(
    tasks: list[Task],
    sprint: Sprint | None,
) -> QueryProjectStatusUseCase:
    task_repo = AsyncMock(spec=TaskRepositoryPort)
    task_repo.list_by_project.return_value = tasks
    sprint_repo = AsyncMock(spec=SprintRepositoryPort)
    sprint_repo.get_active.return_value = sprint
    return QueryProjectStatusUseCase(task_repo=task_repo, sprint_repo=sprint_repo)


PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


# ─────────────────────── test classes ───────────────────────

class TestPointsAggregation:
    async def test_completed_and_remaining_points(self) -> None:
        tasks = [
            make_task(PROJECT_ID, TaskStatus.DONE, points=5),
            make_task(PROJECT_ID, TaskStatus.DONE, points=3),
            make_task(PROJECT_ID, TaskStatus.IN_PROGRESS, points=8),
            make_task(PROJECT_ID, TaskStatus.BACKLOG, points=2),
        ]
        uc = make_use_case(tasks, sprint=None)
        result = await uc.execute(PROJECT_ID)

        assert result.completed_points == 8
        assert result.remaining_points == 10
        assert result.total_points == 18

    async def test_none_points_treated_as_zero(self) -> None:
        tasks = [
            make_task(PROJECT_ID, TaskStatus.DONE, points=0),
        ]
        # override estimated_points to None
        tasks[0].estimated_points = None  # type: ignore[assignment]
        uc = make_use_case(tasks, sprint=None)
        result = await uc.execute(PROJECT_ID)

        assert result.completed_points == 0
        assert result.remaining_points == 0

    async def test_empty_project_returns_zeros(self) -> None:
        uc = make_use_case([], sprint=None)
        result = await uc.execute(PROJECT_ID)

        assert result.completed_points == 0
        assert result.remaining_points == 0
        assert result.total_points == 0


class TestBlockedTaskCount:
    async def test_in_review_high_priority_counts_as_blocked(self) -> None:
        tasks = [
            make_task(PROJECT_ID, TaskStatus.IN_REVIEW, TaskPriority.HIGH),
            make_task(PROJECT_ID, TaskStatus.IN_REVIEW, TaskPriority.CRITICAL),
            make_task(PROJECT_ID, TaskStatus.IN_REVIEW, TaskPriority.MEDIUM),
            make_task(PROJECT_ID, TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
        ]
        uc = make_use_case(tasks, sprint=None)
        result = await uc.execute(PROJECT_ID)

        assert result.blocked_task_count == 2

    async def test_no_blocked_tasks(self) -> None:
        tasks = [
            make_task(PROJECT_ID, TaskStatus.DONE, TaskPriority.CRITICAL),
            make_task(PROJECT_ID, TaskStatus.IN_REVIEW, TaskPriority.LOW),
        ]
        uc = make_use_case(tasks, sprint=None)
        result = await uc.execute(PROJECT_ID)

        assert result.blocked_task_count == 0


class TestActiveSprint:
    async def test_active_sprint_name_returned(self) -> None:
        sprint = make_sprint(PROJECT_ID, name="Alpha Sprint")
        uc = make_use_case([], sprint=sprint)
        result = await uc.execute(PROJECT_ID)

        assert result.active_sprint_name == "Alpha Sprint"

    async def test_no_active_sprint_returns_none(self) -> None:
        uc = make_use_case([], sprint=None)
        result = await uc.execute(PROJECT_ID)

        assert result.active_sprint_name is None
        assert result.days_remaining is None

    async def test_days_remaining_computed_correctly(self) -> None:
        # Add 12-hour buffer so timedelta.days truncation doesn't flip to 4
        future = datetime.now(timezone.utc) + timedelta(days=5, hours=12)
        sprint = make_sprint(PROJECT_ID, end_date=future)
        uc = make_use_case([], sprint=sprint)
        result = await uc.execute(PROJECT_ID)

        assert result.days_remaining == 5

    async def test_days_remaining_never_negative(self) -> None:
        past = datetime.now(timezone.utc) - timedelta(days=2)
        sprint = make_sprint(PROJECT_ID, end_date=past)
        uc = make_use_case([], sprint=sprint)
        result = await uc.execute(PROJECT_ID)

        assert result.days_remaining == 0

    async def test_naive_end_date_handled(self) -> None:
        future = datetime.utcnow() + timedelta(days=3)  # naive
        sprint = make_sprint(PROJECT_ID, end_date=future)
        uc = make_use_case([], sprint=sprint)
        result = await uc.execute(PROJECT_ID)

        assert result.days_remaining is not None
        assert result.days_remaining >= 2  # allow 1-day rounding tolerance
