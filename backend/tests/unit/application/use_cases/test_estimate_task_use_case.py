from __future__ import annotations

import uuid

import pytest

from src.application.commands.estimate_task_command import EstimateTaskCommand
from src.application.use_cases.estimate_task_use_case import EstimateTaskUseCase


class TestEstimateTaskUseCase:
    async def test_execute_returns_estimation(
        self, mock_llm, mock_embedding, mock_vector_store, project_id,
    ) -> None:
        use_case = EstimateTaskUseCase(
            llm=mock_llm, embedding=mock_embedding, vector_store=mock_vector_store,
        )
        command = EstimateTaskCommand(
            project_id=project_id,
            title="Login page",
            description="Implement JWT login with refresh tokens",
        )
        result = await use_case.execute(command)

        assert result.estimation.points in (1, 2, 3, 5, 8, 13, 21)
        assert result.task_id is not None

    async def test_execute_embeds_description(
        self, mock_llm, mock_embedding, mock_vector_store, project_id,
    ) -> None:
        use_case = EstimateTaskUseCase(
            llm=mock_llm, embedding=mock_embedding, vector_store=mock_vector_store,
        )
        command = EstimateTaskCommand(
            project_id=project_id,
            title="Dashboard",
            description="Build metrics dashboard",
        )
        await use_case.execute(command)

        mock_embedding.embed.assert_awaited_once()
        call_text = mock_embedding.embed.call_args[0][0]
        assert "Dashboard" in call_text
        assert "Build metrics dashboard" in call_text

    async def test_execute_searches_vector_store(
        self, mock_llm, mock_embedding, mock_vector_store, project_id,
    ) -> None:
        use_case = EstimateTaskUseCase(
            llm=mock_llm, embedding=mock_embedding, vector_store=mock_vector_store,
        )
        command = EstimateTaskCommand(
            project_id=project_id, title="T", description="D",
        )
        await use_case.execute(command)

        mock_vector_store.search.assert_awaited_once()
        search_kwargs = mock_vector_store.search.call_args[1]
        assert search_kwargs["top_k"] == 5
