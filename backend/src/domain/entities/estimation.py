from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SimilarTask:
    id: uuid.UUID
    title: str
    estimated_points: int
    actual_points: Optional[int]


@dataclass
class PointsBreakdown:
    frontend: int
    backend: int
    testing: int


@dataclass
class Estimation:
    id: uuid.UUID
    task_id: uuid.UUID
    points: int
    confidence: float  # 0.0–1.0
    breakdown: PointsBreakdown
    rationale: str
    similar_tasks: list[SimilarTask] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_high_confidence(self) -> bool:
        # TODO: implement — threshold at 0.7
        raise NotImplementedError
