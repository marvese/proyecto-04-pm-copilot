from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from src.domain.services.estimation_service import EstimationService


class TestEstimationService:
    @pytest.mark.asyncio
    async def test_estimate_calls_llm(
        self, mock_llm, mock_task_repo, mock_vector_store, sample_task
    ) -> None:
        # TODO: once EstimationService.estimate() is implemented:
        # service = EstimationService(mock_llm, mock_task_repo, mock_vector_store)
        # result = await service.estimate(sample_task, similar_chunks=[])
        # assert result.points in (1, 2, 3, 5, 8, 13, 21)
        # mock_llm.complete.assert_called_once()
        pytest.skip("Not implemented yet")

    @pytest.mark.asyncio
    async def test_breakdown_epic_max_15_stories(
        self, mock_llm, mock_task_repo, mock_vector_store, sample_task
    ) -> None:
        # TODO: assert len(stories) <= 15
        pytest.skip("Not implemented yet")
