from __future__ import annotations

import uuid
import pytest

from src.application.use_cases.create_task_use_case import CreateTaskUseCase
from src.application.commands.create_task_command import CreateTaskCommand
from src.domain.entities.task import TaskType, TaskPriority, TaskStatus, JiraSyncStatus


class TestCreateTaskUseCase:
    @pytest.mark.asyncio
    async def test_creates_task_with_backlog_status(self, mock_task_repo, project_id) -> None:
        mock_task_repo.save.side_effect = lambda t: t
        use_case = CreateTaskUseCase(mock_task_repo)
        command = CreateTaskCommand(project_id=project_id, title="New task", description="desc")

        saved = await use_case.execute(command)

        assert saved.status == TaskStatus.BACKLOG

    @pytest.mark.asyncio
    async def test_creates_task_with_local_only_sync(self, mock_task_repo, project_id) -> None:
        mock_task_repo.save.side_effect = lambda t: t
        use_case = CreateTaskUseCase(mock_task_repo)
        command = CreateTaskCommand(project_id=project_id, title="New task", description="desc")

        saved = await use_case.execute(command)

        assert saved.jira_sync_status == JiraSyncStatus.LOCAL_ONLY

    @pytest.mark.asyncio
    async def test_creates_task_with_given_fields(self, mock_task_repo, project_id) -> None:
        mock_task_repo.save.side_effect = lambda t: t
        use_case = CreateTaskUseCase(mock_task_repo)
        sprint_id = uuid.uuid4()
        command = CreateTaskCommand(
            project_id=project_id,
            title="Auth feature",
            description="Implement JWT",
            type=TaskType.STORY,
            priority=TaskPriority.HIGH,
            estimated_points=5,
            sprint_id=sprint_id,
            tags=["backend", "security"],
        )

        saved = await use_case.execute(command)

        assert saved.title == "Auth feature"
        assert saved.type == TaskType.STORY
        assert saved.priority == TaskPriority.HIGH
        assert saved.estimated_points == 5
        assert saved.sprint_id == sprint_id
        assert saved.tags == ["backend", "security"]

    @pytest.mark.asyncio
    async def test_generates_new_uuid_each_call(self, mock_task_repo, project_id) -> None:
        mock_task_repo.save.side_effect = lambda t: t
        use_case = CreateTaskUseCase(mock_task_repo)
        command = CreateTaskCommand(project_id=project_id, title="T1", description="d")

        t1 = await use_case.execute(command)
        t2 = await use_case.execute(command)

        assert t1.id != t2.id

    @pytest.mark.asyncio
    async def test_calls_repo_save_once(self, mock_task_repo, project_id) -> None:
        mock_task_repo.save.side_effect = lambda t: t
        use_case = CreateTaskUseCase(mock_task_repo)
        command = CreateTaskCommand(project_id=project_id, title="T", description="d")

        await use_case.execute(command)

        mock_task_repo.save.assert_called_once()
