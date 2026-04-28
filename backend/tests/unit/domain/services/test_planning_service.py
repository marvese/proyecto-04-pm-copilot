from __future__ import annotations

import pytest

from src.domain.services.planning_service import PlanningService


class TestPlanningService:
    @pytest.mark.asyncio
    async def test_plan_sprint_respects_capacity(
        self, mock_llm, mock_task_repo
    ) -> None:
        # TODO: assert sum(t.estimated_points for t in selected) <= capacity
        pytest.skip("Not implemented yet")

    def test_compute_velocity_empty(self, mock_llm, mock_task_repo) -> None:
        # TODO: assert compute_velocity([]) returns 0 or raises gracefully
        pytest.skip("Not implemented yet")
