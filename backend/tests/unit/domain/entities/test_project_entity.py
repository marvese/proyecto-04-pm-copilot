from __future__ import annotations

import uuid
from datetime import datetime

import pytest

from src.domain.entities.project import Sprint, SprintStatus, Project


def make_sprint(status: SprintStatus = SprintStatus.ACTIVE) -> Sprint:
    return Sprint(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        name="Sprint 1",
        goal=None,
        status=status,
        capacity_points=None,
    )


def make_project() -> Project:
    return Project(
        id=uuid.uuid4(),
        name="PM Copilot",
        description="Test project",
        jira_project_key="PMCP",
        confluence_space_key="PBPMIA",
        github_repo=None,
    )


class TestSprintIsActive:
    def test_active_sprint_returns_true(self) -> None:
        assert make_sprint(SprintStatus.ACTIVE).is_active() is True

    def test_planned_sprint_returns_false(self) -> None:
        assert make_sprint(SprintStatus.PLANNED).is_active() is False

    def test_completed_sprint_returns_false(self) -> None:
        assert make_sprint(SprintStatus.COMPLETED).is_active() is False


class TestProjectActiveSprint:
    def test_returns_active_sprint(self) -> None:
        project = make_project()
        sprints = [
            make_sprint(SprintStatus.COMPLETED),
            make_sprint(SprintStatus.ACTIVE),
            make_sprint(SprintStatus.PLANNED),
        ]
        result = project.active_sprint(sprints)
        assert result is not None
        assert result.status == SprintStatus.ACTIVE

    def test_returns_none_when_no_active(self) -> None:
        project = make_project()
        sprints = [
            make_sprint(SprintStatus.COMPLETED),
            make_sprint(SprintStatus.PLANNED),
        ]
        assert project.active_sprint(sprints) is None

    def test_returns_none_for_empty_list(self) -> None:
        assert make_project().active_sprint([]) is None

    def test_returns_first_active_when_multiple(self) -> None:
        project = make_project()
        first = make_sprint(SprintStatus.ACTIVE)
        second = make_sprint(SprintStatus.ACTIVE)
        result = project.active_sprint([first, second])
        assert result is first
