from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.sync_jira_use_case import SyncJiraUseCase, SyncJiraResult
from src.domain.entities.task import (
    JiraSyncStatus,
    Task,
    TaskPriority,
    TaskStatus,
    TaskType,
)


def _make_task(jira_key: str | None = None, sync_status: JiraSyncStatus = JiraSyncStatus.PENDING) -> Task:
    return Task(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        title="Sample Task",
        description="Description",
        type=TaskType.STORY,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        jira_key=jira_key,
        jira_sync_status=sync_status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_task_repo():
    repo = AsyncMock()
    repo.save = AsyncMock(side_effect=lambda t: t)
    return repo


@pytest.fixture
def mock_jira():
    jira = AsyncMock()
    jira.create_issue = AsyncMock(return_value="PMCP-99")
    jira.update_issue = AsyncMock(return_value=None)
    return jira


@pytest.fixture
def use_case(mock_task_repo, mock_jira):
    return SyncJiraUseCase(task_repo=mock_task_repo, jira_port=mock_jira)


class TestSyncJiraUseCaseExecute:
    @pytest.mark.asyncio
    async def test_execute_creates_new_issues_for_tasks_without_jira_key(
        self, use_case, mock_task_repo, mock_jira
    ):
        tasks = [_make_task(jira_key=None), _make_task(jira_key=None)]
        mock_task_repo.list_pending_jira_sync = AsyncMock(return_value=tasks)

        result = await use_case.execute(uuid.uuid4(), "PMCP")

        assert result.pushed_count == 2
        assert result.failed_count == 0
        assert mock_jira.create_issue.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_updates_existing_issues_when_jira_key_present(
        self, use_case, mock_task_repo, mock_jira
    ):
        task = _make_task(jira_key="PMCP-10")
        mock_task_repo.list_pending_jira_sync = AsyncMock(return_value=[task])

        result = await use_case.execute(uuid.uuid4(), "PMCP")

        mock_jira.update_issue.assert_called_once()
        mock_jira.create_issue.assert_not_called()
        assert result.pushed_count == 1

    @pytest.mark.asyncio
    async def test_execute_sets_synced_status_on_success(
        self, use_case, mock_task_repo, mock_jira
    ):
        task = _make_task(jira_key=None)
        mock_task_repo.list_pending_jira_sync = AsyncMock(return_value=[task])
        saved_tasks = []
        mock_task_repo.save = AsyncMock(side_effect=lambda t: saved_tasks.append(t) or t)

        await use_case.execute(uuid.uuid4(), "PMCP")

        assert saved_tasks[0].jira_sync_status == JiraSyncStatus.SYNCED
        assert saved_tasks[0].jira_key == "PMCP-99"

    @pytest.mark.asyncio
    async def test_execute_sets_failed_status_when_jira_raises(
        self, use_case, mock_task_repo, mock_jira
    ):
        task = _make_task(jira_key=None)
        mock_task_repo.list_pending_jira_sync = AsyncMock(return_value=[task])
        mock_jira.create_issue = AsyncMock(side_effect=Exception("Jira unavailable"))
        saved_tasks = []
        mock_task_repo.save = AsyncMock(side_effect=lambda t: saved_tasks.append(t) or t)

        result = await use_case.execute(uuid.uuid4(), "PMCP")

        assert result.failed_count == 1
        assert result.pushed_count == 0
        assert saved_tasks[0].jira_sync_status == JiraSyncStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_returns_zero_counts_when_no_pending(
        self, use_case, mock_task_repo
    ):
        mock_task_repo.list_pending_jira_sync = AsyncMock(return_value=[])

        result = await use_case.execute(uuid.uuid4(), "PMCP")

        assert result == SyncJiraResult(pushed_count=0, pulled_count=0, conflict_count=0, failed_count=0)

    @pytest.mark.asyncio
    async def test_execute_continues_after_partial_failure(
        self, use_case, mock_task_repo, mock_jira
    ):
        tasks = [_make_task(jira_key=None), _make_task(jira_key=None)]
        mock_task_repo.list_pending_jira_sync = AsyncMock(return_value=tasks)
        mock_jira.create_issue = AsyncMock(
            side_effect=["PMCP-1", Exception("fail")]
        )

        result = await use_case.execute(uuid.uuid4(), "PMCP")

        assert result.pushed_count == 1
        assert result.failed_count == 1


class TestSyncJiraUseCaseSyncSingle:
    @pytest.mark.asyncio
    async def test_sync_single_creates_issue_when_no_jira_key(
        self, use_case, mock_task_repo, mock_jira
    ):
        task = _make_task(jira_key=None)
        mock_task_repo.get_by_id = AsyncMock(return_value=task)
        saved = []
        mock_task_repo.save = AsyncMock(side_effect=lambda t: saved.append(t) or t)

        await use_case.sync_single(task.id, "PMCP")

        mock_jira.create_issue.assert_called_once()
        assert saved[0].jira_key == "PMCP-99"
        assert saved[0].jira_sync_status == JiraSyncStatus.SYNCED

    @pytest.mark.asyncio
    async def test_sync_single_noop_when_task_not_found(
        self, use_case, mock_task_repo, mock_jira
    ):
        mock_task_repo.get_by_id = AsyncMock(return_value=None)

        await use_case.sync_single(uuid.uuid4(), "PMCP")

        mock_jira.create_issue.assert_not_called()
        mock_task_repo.save.assert_not_called()
