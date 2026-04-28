from __future__ import annotations

from ...domain.ports.llm_port import LLMPort
from ...domain.ports.sprint_repository_port import SprintRepositoryPort
from ...domain.ports.task_repository_port import TaskRepositoryPort
from ...domain.services.planning_service import PlanningService
from ..commands.plan_sprint_command import PlanSprintCommand, PlanSprintResult


class PlanSprintUseCase:
    def __init__(
        self,
        llm_port: LLMPort,
        task_repo: TaskRepositoryPort,
        sprint_repo: SprintRepositoryPort,
    ) -> None:
        self._planning_service = PlanningService(llm_port, task_repo)
        self._task_repo = task_repo
        self._sprint_repo = sprint_repo

    async def execute(self, command: PlanSprintCommand) -> PlanSprintResult:
        # TODO: implement
        # 1. Fetch sprint and backlog tasks by IDs
        # 2. Call PlanningService.plan_sprint()
        # 3. Return PlanSprintResult
        raise NotImplementedError
