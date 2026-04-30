from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock

import pytest

from src.domain.entities.task import Task, TaskType, TaskStatus, TaskPriority
from src.domain.ports.llm_port import LLMPort, LLMResponse
from src.domain.ports.vector_store_port import SearchResult
from src.domain.services.estimation_service import EstimationService


def _llm_response(payload: dict) -> LLMResponse:
    return LLMResponse(
        content=json.dumps(payload),
        model="test", provider="mock", input_tokens=10, output_tokens=20,
    )


def _make_task(title: str = "Login page", description: str = "Implement JWT auth") -> Task:
    return Task(
        id=uuid.uuid4(), project_id=uuid.uuid4(),
        title=title, description=description,
        type=TaskType.STORY, status=TaskStatus.BACKLOG, priority=TaskPriority.MEDIUM,
    )


def _make_service(payload: dict) -> tuple[EstimationService, AsyncMock]:
    mock_llm = AsyncMock(spec=LLMPort)
    mock_llm.complete.return_value = _llm_response(payload)
    return EstimationService(llm=mock_llm), mock_llm


class TestEstimationService:
    async def test_estimate_calls_llm(self, mock_llm, mock_task_repo, mock_vector_store, sample_task) -> None:
        service = EstimationService(llm=mock_llm)
        result = await service.estimate(sample_task, similar_chunks=[])

        mock_llm.complete.assert_awaited_once()
        assert result.points in (1, 2, 3, 5, 8, 13, 21)
        assert 0.0 <= result.confidence <= 1.0

    async def test_estimate_returns_correct_points(self) -> None:
        service, _ = _make_service({
            "points": 8, "confidence": 0.9, "rationale": "Complex",
            "breakdown": {"frontend": 2, "backend": 5, "testing": 1},
            "risks": ["DB migration"], "similar_tasks": [],
        })
        result = await service.estimate(_make_task(), similar_chunks=[])
        assert result.points == 8
        assert result.is_high_confidence() is True

    async def test_estimate_snaps_non_fibonacci_to_nearest(self) -> None:
        service, _ = _make_service({
            "points": 4, "confidence": 0.7, "rationale": "x",
            "breakdown": {"frontend": 1, "backend": 2, "testing": 1},
            "risks": [], "similar_tasks": [],
        })
        result = await service.estimate(_make_task(), similar_chunks=[])
        assert result.points in (1, 2, 3, 5, 8, 13, 21)

    async def test_estimate_invalid_json_raises_value_error(self) -> None:
        mock_llm = AsyncMock(spec=LLMPort)
        mock_llm.complete.return_value = LLMResponse(
            content="not json", model="test", provider="mock", input_tokens=5, output_tokens=5,
        )
        with pytest.raises(ValueError, match="invalid JSON"):
            await EstimationService(llm=mock_llm).estimate(_make_task(), similar_chunks=[])

    async def test_estimate_uses_similar_chunks_in_prompt(self) -> None:
        service, mock_llm = _make_service({
            "points": 3, "confidence": 0.75, "rationale": "small",
            "breakdown": {"frontend": 1, "backend": 1, "testing": 1},
            "risks": [], "similar_tasks": [],
        })
        chunks = [SearchResult(id="1", content="Add user login", score=0.9,
                               metadata={"estimated_points": 5})]
        await service.estimate(_make_task(), similar_chunks=chunks)
        call_args = mock_llm.complete.call_args[0][0]
        assert "Add user login" in call_args.prompt

    async def test_is_high_confidence_threshold(self) -> None:
        service, _ = _make_service({
            "points": 5, "confidence": 0.65, "rationale": "x",
            "breakdown": {"frontend": 1, "backend": 3, "testing": 1},
            "risks": [], "similar_tasks": [],
        })
        result = await service.estimate(_make_task(), similar_chunks=[])
        assert result.is_high_confidence() is False

    async def test_breakdown_epic_max_15_stories(self, mock_llm, mock_task_repo, mock_vector_store, sample_task) -> None:
        stories_payload = [
            {"title": f"Story {i}", "description": f"Desc {i}", "estimated_points": 3}
            for i in range(20)
        ]
        mock_llm.complete.return_value = _llm_response({"stories": stories_payload})
        service = EstimationService(llm=mock_llm)
        sample_task.type = TaskType.EPIC

        stories = await service.breakdown_epic(sample_task)
        assert len(stories) <= 15

    async def test_breakdown_epic_returns_story_type(self) -> None:
        service, _ = _make_service({"stories": [
            {"title": "Login", "description": "JWT auth", "estimated_points": 5},
        ]})
        task = _make_task()
        task.type = TaskType.EPIC
        stories = await service.breakdown_epic(task)
        assert all(s.type == TaskType.STORY for s in stories)

    async def test_breakdown_epic_invalid_json_raises(self) -> None:
        mock_llm = AsyncMock(spec=LLMPort)
        mock_llm.complete.return_value = LLMResponse(
            content="broken", model="test", provider="mock", input_tokens=5, output_tokens=5,
        )
        with pytest.raises(ValueError, match="invalid JSON"):
            await EstimationService(llm=mock_llm).breakdown_epic(_make_task())
