from __future__ import annotations

from ..entities.project import Sprint
from ..entities.task import Task
from ..ports.llm_port import LLMPort
from ..ports.task_repository_port import TaskRepositoryPort


class PlanningService:
    """Assists in sprint planning by selecting tasks that fit team capacity."""

    def __init__(self, llm_port: LLMPort, task_repo: TaskRepositoryPort) -> None:
        self._llm = llm_port
        self._task_repo = task_repo

    async def plan_sprint(
        self,
        backlog: list[Task],
        sprint: Sprint,
        capacity_points: int,
    ) -> tuple[list[Task], list[Task], str]:
        # TODO: implement
        # Returns: (selected_tasks, excluded_tasks, justification_markdown)
        raise NotImplementedError

    def compute_velocity(self, past_sprints: list[Sprint]) -> float:
        # TODO: implement — average velocity over last N sprints
        raise NotImplementedError
