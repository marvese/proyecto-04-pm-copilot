from __future__ import annotations

import json
import uuid
from datetime import datetime

from ..entities.estimation import Estimation, PointsBreakdown, SimilarTask
from ..entities.task import FIBONACCI_POINTS, Task, TaskStatus, TaskType, TaskPriority
from ..ports.llm_port import LLMPort, LLMRequest, LLMTaskType
from ..ports.vector_store_port import SearchResult

_ESTIMATION_SYSTEM = (
    "You are a senior software engineer estimating story points. "
    "Use only Fibonacci numbers. Respond only with valid JSON."
)

_ESTIMATION_PROMPT = """\
Estimate story points (Fibonacci scale: 1, 2, 3, 5, 8, 13, 21) for this task.

## Task
Title: {title}
Description: {description}

## Similar Historical Tasks
{similar_section}

## Required JSON response (no extra text)
{{
  "points": <fibonacci int>,
  "confidence": <float 0.0-1.0>,
  "rationale": "<explanation>",
  "breakdown": {{"frontend": <int>, "backend": <int>, "testing": <int>}},
  "risks": ["<risk>"],
  "similar_tasks": []
}}
"""

_BREAKDOWN_SYSTEM = (
    "You are a senior product manager decomposing epics into user stories. "
    "Respond only with valid JSON."
)

_BREAKDOWN_PROMPT = """\
Decompose this epic into independent user stories (maximum 15).

## Epic
Title: {title}
Description: {description}

## Required JSON response (no extra text)
{{
  "stories": [
    {{"title": "<title>", "description": "<what to implement>", "estimated_points": <fibonacci int or null>}}
  ]
}}
"""


class EstimationService:
    """Coordinates LLM calls to produce estimations and epic breakdowns.

    Lives in the domain — only depends on ports, never on concrete adapters.
    """

    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    async def estimate(self, task: Task, similar_chunks: list[SearchResult]) -> Estimation:
        similar_section = _build_similar_section(similar_chunks)
        prompt = _ESTIMATION_PROMPT.format(
            title=task.title,
            description=task.description,
            similar_section=similar_section,
        )
        request = LLMRequest(
            prompt=prompt,
            task_type=LLMTaskType.REASONING,
            system=_ESTIMATION_SYSTEM,
            max_tokens=512,
            json_mode=True,
        )
        response = await self._llm.complete(request)
        return _parse_estimation(response.content, task_id=task.id)

    async def breakdown_epic(self, epic: Task) -> list[Task]:
        prompt = _BREAKDOWN_PROMPT.format(title=epic.title, description=epic.description)
        request = LLMRequest(
            prompt=prompt,
            task_type=LLMTaskType.GENERATION_LONG,
            system=_BREAKDOWN_SYSTEM,
            max_tokens=2048,
            json_mode=True,
        )
        response = await self._llm.complete(request)
        return _parse_breakdown(response.content, project_id=epic.project_id)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_similar_section(chunks: list[SearchResult]) -> str:
    if not chunks:
        return "No similar tasks found."
    lines = []
    for i, chunk in enumerate(chunks, 1):
        points = chunk.metadata.get("estimated_points", "?")
        lines.append(f"{i}. {chunk.content[:120]} — {points} SP")
    return "\n".join(lines)


def _parse_estimation(raw: str, task_id: uuid.UUID) -> Estimation:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON for estimation: {exc}\nRaw: {raw[:200]}")

    points = int(data.get("points", 0))
    if points not in FIBONACCI_POINTS:
        # Snap to nearest Fibonacci value
        points = min(FIBONACCI_POINTS, key=lambda x: abs(x - points))

    confidence = float(data.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))

    bd = data.get("breakdown", {})
    breakdown = PointsBreakdown(
        frontend=int(bd.get("frontend", 0)),
        backend=int(bd.get("backend", 0)),
        testing=int(bd.get("testing", 0)),
    )

    similar_tasks = [
        SimilarTask(
            id=uuid.uuid4(),
            title=st.get("title", ""),
            estimated_points=int(st.get("estimated_points", 0)),
            actual_points=st.get("actual_points"),
        )
        for st in data.get("similar_tasks", [])
    ]

    return Estimation(
        id=uuid.uuid4(),
        task_id=task_id,
        points=points,
        confidence=confidence,
        breakdown=breakdown,
        rationale=str(data.get("rationale", "")),
        similar_tasks=similar_tasks,
        risks=list(data.get("risks", [])),
    )


def _parse_breakdown(raw: str, project_id: uuid.UUID) -> list[Task]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON for breakdown: {exc}\nRaw: {raw[:200]}")

    stories_data = data.get("stories", [])[:15]
    now = datetime.utcnow()
    tasks = []
    for story in stories_data:
        pts = story.get("estimated_points")
        if pts is not None:
            pts = int(pts)
            if pts not in FIBONACCI_POINTS:
                pts = min(FIBONACCI_POINTS, key=lambda x: abs(x - pts))
        tasks.append(Task(
            id=uuid.uuid4(),
            project_id=project_id,
            title=str(story.get("title", "")),
            description=str(story.get("description", "")),
            type=TaskType.STORY,
            status=TaskStatus.BACKLOG,
            priority=TaskPriority.MEDIUM,
            estimated_points=pts,
            created_at=now,
            updated_at=now,
        ))
    return tasks
