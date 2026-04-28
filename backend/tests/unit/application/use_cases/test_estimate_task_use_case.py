from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.estimate_task_use_case import EstimateTaskUseCase
from src.application.commands.estimate_task_command import EstimateTaskCommand
import uuid


class TestEstimateTaskUseCase:
    @pytest.mark.asyncio
    async def test_execute_returns_estimation(
        self,
        mock_llm,
        mock_task_repo,
        mock_embedding,
        mock_vector_store,
        project_id,
    ) -> None:
        # TODO: once execute() is implemented:
        # use_case = EstimateTaskUseCase(mock_llm, mock_task_repo, mock_embedding, mock_vector_store)
        # command = EstimateTaskCommand(project_id=project_id, title="Login page", description="Implement JWT login")
        # result = await use_case.execute(command)
        # assert result.estimation.points in (1, 2, 3, 5, 8, 13, 21)
        pytest.skip("Not implemented yet")

    @pytest.mark.asyncio
    async def test_execute_embeds_description(
        self, mock_llm, mock_task_repo, mock_embedding, mock_vector_store, project_id
    ) -> None:
        # TODO: assert mock_embedding.embed.called_once_with(command.description)
        pytest.skip("Not implemented yet")
