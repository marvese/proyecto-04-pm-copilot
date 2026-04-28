from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from ...domain.entities.estimation import Estimation


@dataclass
class EstimateTaskCommand:
    project_id: uuid.UUID
    title: str
    description: str
    acceptance_criteria: Optional[str] = None
    component_tags: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.component_tags is None:
            self.component_tags = []


@dataclass
class EstimateTaskResult:
    estimation: Estimation
    task_id: uuid.UUID
