from __future__ import annotations

import uuid
import pytest

from src.application.use_cases.update_task_use_case import UpdateTaskUseCase, UpdateTaskCommand
from src.domain.entities.task import TaskStatus, TaskPriority
from src.domain.exceptions import DomainError


class TestUpdateTaskUseCase:
    @pytest.mark.asyncio
    async def test_updates_status(self, mock_task_repo, sample_task) -> None:
        mock_task_repo.get_by_id.return_value = sample_task
        mock_task_repo.save.side_effect = lambda t: t
        use_case = UpdateTaskUseCase(mock_task_repo)

        updated = await use_case.execute(
            UpdateTaskCommand(task_id=sample_task.id, updates={"status": TaskStatus.IN_PROGRESS})
        )

        assert updated.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_updates_multiple_fields(self, mock_task_repo, sample_task) -> None:
        mock_task_repo.get_by_id.return_value = sample_task
        mock_task_repo.save.side_effect = lambda t: t
        use_case = UpdateTaskUseCase(mock_task_repo)

        updated = await use_case.execute(
            UpdateTaskCommand(
                task_id=sample_task.id,
                updates={"title": "New title", "priority": TaskPriority.CRITICAL},
            )
        )

        assert updated.title == "New title"
        assert updated.priority == TaskPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_raises_domain_error_when_not_found(self, mock_task_repo) -> None:
        mock_task_repo.get_by_id.return_value = None
        use_case = UpdateTaskUseCase(mock_task_repo)

        with pytest.raises(DomainError):
            await use_case.execute(
                UpdateTaskCommand(task_id=uuid.uuid4(), updates={"status": TaskStatus.DONE})
            )

    @pytest.mark.asyncio
    async def test_ignores_unknown_fields(self, mock_task_repo, sample_task) -> None:
        mock_task_repo.get_by_id.return_value = sample_task
        mock_task_repo.save.side_effect = lambda t: t
        use_case = UpdateTaskUseCase(mock_task_repo)

        updated = await use_case.execute(
            UpdateTaskCommand(task_id=sample_task.id, updates={"nonexistent_field": "value"})
        )

        assert updated.id == sample_task.id

    @pytest.mark.asyncio
    async def test_calls_repo_save_once(self, mock_task_repo, sample_task) -> None:
        mock_task_repo.get_by_id.return_value = sample_task
        mock_task_repo.save.side_effect = lambda t: t
        use_case = UpdateTaskUseCase(mock_task_repo)

        await use_case.execute(
            UpdateTaskCommand(task_id=sample_task.id, updates={"status": TaskStatus.DONE})
        )

        mock_task_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_updated_at(self, mock_task_repo, sample_task) -> None:
        original_updated_at = sample_task.updated_at
        mock_task_repo.get_by_id.return_value = sample_task
        mock_task_repo.save.side_effect = lambda t: t
        use_case = UpdateTaskUseCase(mock_task_repo)

        updated = await use_case.execute(
            UpdateTaskCommand(task_id=sample_task.id, updates={"status": TaskStatus.DONE})
        )

        assert updated.updated_at >= original_updated_at
