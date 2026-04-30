from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SprintStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class Sprint:
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    goal: Optional[str]
    status: SprintStatus
    capacity_points: Optional[int]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def velocity(self) -> Optional[float]:
        if not self.capacity_points:
            return None
        return None  # requires actual completed points — computed externally

    def is_active(self) -> bool:
        return self.status == SprintStatus.ACTIVE


@dataclass
class Project:
    id: uuid.UUID
    name: str
    description: str
    jira_project_key: Optional[str]
    confluence_space_key: Optional[str]
    github_repo: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def active_sprint(self, sprints: list[Sprint]) -> Optional[Sprint]:
        for sprint in sprints:
            if sprint.is_active():
                return sprint
        return None
