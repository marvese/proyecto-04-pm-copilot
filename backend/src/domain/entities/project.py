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
        # TODO: implement — returns completed points / capacity
        raise NotImplementedError

    def is_active(self) -> bool:
        # TODO: implement
        raise NotImplementedError


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
        # TODO: implement — returns the single active sprint or None
        raise NotImplementedError
