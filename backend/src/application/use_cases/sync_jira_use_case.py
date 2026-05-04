from __future__ import annotations

import uuid
from dataclasses import dataclass

from ...domain.entities.task import JiraSyncStatus, Task
from ...domain.ports.jira_port import JiraPort
from ...domain.ports.task_repository_port import TaskRepositoryPort


@dataclass
class SyncJiraResult:
    pushed_count: int
    pulled_count: int
    conflict_count: int
    failed_count: int


def _task_to_jira_fields(task: Task) -> dict:
    """Map domain Task fields to Jira issue fields."""
    priority_map = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Highest",
    }
    issuetype_map = {
        "story": "Story",
        "bug": "Bug",
        "task": "Task",
        "epic": "Epic",
    }
    fields: dict = {
        "summary": task.title,
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": task.description or ""}],
                }
            ],
        },
        "issuetype": {"name": issuetype_map.get(task.type.value, "Story")},
        "priority": {"name": priority_map.get(task.priority.value, "Medium")},
    }
    if task.estimated_points is not None:
        fields["story_points"] = task.estimated_points
    return fields


class SyncJiraUseCase:
    """Push local PENDING tasks to Jira and update their sync status."""

    def __init__(self, task_repo: TaskRepositoryPort, jira_port: JiraPort) -> None:
        self._task_repo = task_repo
        self._jira = jira_port

    async def execute(self, project_id: uuid.UUID, jira_project_key: str) -> SyncJiraResult:
        pending = await self._task_repo.list_pending_jira_sync(project_id)
        pushed = 0
        failed = 0

        for task in pending:
            try:
                fields = _task_to_jira_fields(task)
                if task.jira_key is None:
                    jira_key = await self._jira.create_issue(jira_project_key, fields)
                    task.jira_key = jira_key
                else:
                    await self._jira.update_issue(task.jira_key, fields)
                task.jira_sync_status = JiraSyncStatus.SYNCED
                pushed += 1
            except Exception:
                task.jira_sync_status = JiraSyncStatus.FAILED
                failed += 1
            await self._task_repo.save(task)

        return SyncJiraResult(
            pushed_count=pushed,
            pulled_count=0,
            conflict_count=0,
            failed_count=failed,
        )

    async def sync_single(self, task_id: uuid.UUID, jira_project_key: str) -> None:
        task = await self._task_repo.get_by_id(task_id)
        if task is None:
            return
        try:
            fields = _task_to_jira_fields(task)
            if task.jira_key is None:
                jira_key = await self._jira.create_issue(jira_project_key, fields)
                task.jira_key = jira_key
            else:
                await self._jira.update_issue(task.jira_key, fields)
            task.jira_sync_status = JiraSyncStatus.SYNCED
        except Exception:
            task.jira_sync_status = JiraSyncStatus.FAILED
        await self._task_repo.save(task)
