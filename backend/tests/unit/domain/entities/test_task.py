from __future__ import annotations

import uuid
import pytest
from src.domain.entities.task import (
    Task, TaskType, TaskStatus, TaskPriority, JiraSyncStatus, FIBONACCI_POINTS
)


def make_task(**kwargs) -> Task:
    defaults = dict(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        title="Test task",
        description="desc",
        type=TaskType.STORY,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
    )
    defaults.update(kwargs)
    return Task(**defaults)


class TestTaskDefaults:
    def test_jira_sync_status_default(self) -> None:
        task = make_task()
        assert task.jira_sync_status == JiraSyncStatus.LOCAL_ONLY

    def test_tags_default_empty(self) -> None:
        task = make_task()
        assert task.tags == []

    def test_optional_fields_default_none(self) -> None:
        task = make_task()
        assert task.estimated_points is None
        assert task.actual_points is None
        assert task.sprint_id is None
        assert task.jira_key is None


class TestIsValidStoryPoints:
    def test_all_fibonacci_values_are_valid(self) -> None:
        task = make_task()
        for pts in FIBONACCI_POINTS:
            assert task.is_valid_story_points(pts) is True

    def test_non_fibonacci_values_are_invalid(self) -> None:
        task = make_task()
        for pts in (0, 4, 6, 7, 9, 10, 15, 100):
            assert task.is_valid_story_points(pts) is False

    def test_negative_points_invalid(self) -> None:
        task = make_task()
        assert task.is_valid_story_points(-1) is False


class TestMarkDone:
    def test_sets_status_to_done(self) -> None:
        task = make_task(status=TaskStatus.IN_REVIEW)
        task.mark_done(actual_points=5)
        assert task.status == TaskStatus.DONE

    def test_records_actual_points(self) -> None:
        task = make_task()
        task.mark_done(actual_points=8)
        assert task.actual_points == 8

    def test_updates_updated_at(self) -> None:
        from datetime import datetime
        before = datetime.utcnow()
        task = make_task()
        task.mark_done(actual_points=3)
        assert task.updated_at >= before

    def test_mark_done_from_any_status(self) -> None:
        for status in TaskStatus:
            task = make_task(status=status)
            task.mark_done(actual_points=1)
            assert task.status == TaskStatus.DONE
