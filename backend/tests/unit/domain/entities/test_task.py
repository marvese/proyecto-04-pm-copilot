from __future__ import annotations

import uuid
import pytest
from src.domain.entities.task import (
    Task, TaskType, TaskStatus, TaskPriority, JiraSyncStatus, FIBONACCI_POINTS
)


class TestTask:
    def test_fibonacci_points_valid(self) -> None:
        # TODO: once is_valid_story_points is implemented, assert True for each value in FIBONACCI_POINTS
        assert FIBONACCI_POINTS == (1, 2, 3, 5, 8, 13, 21)

    def test_fibonacci_points_invalid(self) -> None:
        # TODO: assert is_valid_story_points(4) returns False
        pass

    def test_task_defaults(self, sample_task: Task) -> None:
        assert sample_task.jira_sync_status == JiraSyncStatus.LOCAL_ONLY
        assert sample_task.tags == ["backend", "llm"]
        assert sample_task.jira_key is None
