from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from ...domain.entities.task import TaskType, TaskPriority


@dataclass
class CreateTaskCommand:
    project_id: uuid.UUID
    title: str
    description: str
    type: TaskType = TaskType.TASK
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_points: Optional[int] = None
    sprint_id: Optional[uuid.UUID] = None
    tags: list[str] = field(default_factory=list)
