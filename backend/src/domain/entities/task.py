from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskType(str, Enum):
    STORY = "story"
    BUG = "bug"
    TASK = "task"
    EPIC = "epic"


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class JiraSyncStatus(str, Enum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    LOCAL_ONLY = "local_only"


FIBONACCI_POINTS: tuple[int, ...] = (1, 2, 3, 5, 8, 13, 21)


@dataclass
class Task:
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str
    type: TaskType
    status: TaskStatus
    priority: TaskPriority
    estimated_points: Optional[int] = None
    actual_points: Optional[int] = None
    sprint_id: Optional[uuid.UUID] = None
    assignee_id: Optional[uuid.UUID] = None
    jira_key: Optional[str] = None
    jira_sync_status: JiraSyncStatus = JiraSyncStatus.LOCAL_ONLY
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_valid_story_points(self, points: int) -> bool:
        return points in FIBONACCI_POINTS

    def mark_done(self, actual_points: int) -> None:
        self.status = TaskStatus.DONE
        self.actual_points = actual_points
        self.updated_at = datetime.utcnow()
