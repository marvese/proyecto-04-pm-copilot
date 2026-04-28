from __future__ import annotations

import uuid
import pytest

from src.application.use_cases.create_task_use_case import CreateTaskUseCase
from src.application.commands.create_task_command import CreateTaskCommand
from src.domain.entities.task import TaskType, TaskPriority, JiraSyncStatus


class TestCreateTaskUseCase:
    @pytest.mark.asyncio
    async def test_creates_task_with_local_only_sync(
        self, mock_task_repo, project_id
    ) -> None:
        # TODO: once execute() is implemented:
        # use_case = CreateTaskUseCase(mock_task_repo)
        # command = CreateTaskCommand(project_id=project_id, title="New task", description="desc")
        # saved_task = await use_case.execute(command)
        # assert saved_task.jira_sync_status == JiraSyncStatus.LOCAL_ONLY
        # mock_task_repo.save.assert_called_once()
        pytest.skip("Not implemented yet")
