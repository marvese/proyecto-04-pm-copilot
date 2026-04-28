from __future__ import annotations

import uuid
from dataclasses import dataclass

from ...domain.entities.task import Task


@dataclass
class PlanSprintCommand:
    project_id: uuid.UUID
    sprint_id: uuid.UUID
    capacity_points: int
    backlog_task_ids: list[uuid.UUID]


@dataclass
class PlanSprintResult:
    selected_task_ids: list[uuid.UUID]
    excluded_task_ids: list[uuid.UUID]
    justification: str
    total_points: int
