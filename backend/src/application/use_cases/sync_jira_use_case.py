from __future__ import annotations

import uuid
from dataclasses import dataclass

from ...domain.ports.jira_port import JiraPort
from ...domain.ports.task_repository_port import TaskRepositoryPort


@dataclass
class SyncJiraResult:
    pushed_count: int
    pulled_count: int
    conflict_count: int
    failed_count: int


class SyncJiraUseCase:
    """Bidirectional sync between local tasks and Jira issues."""

    def __init__(self, task_repo: TaskRepositoryPort, jira_port: JiraPort) -> None:
        self._task_repo = task_repo
        self._jira = jira_port

    async def execute(self, project_id: uuid.UUID) -> SyncJiraResult:
        # TODO: implement
        # 1. Push local PENDING tasks to Jira
        # 2. Pull recent Jira changes
        # 3. Resolve conflicts (Jira wins per spec)
        # 4. Return SyncJiraResult
        raise NotImplementedError

    async def sync_single(self, task_id: uuid.UUID) -> None:
        # TODO: implement — immediate sync for a single task
        raise NotImplementedError
