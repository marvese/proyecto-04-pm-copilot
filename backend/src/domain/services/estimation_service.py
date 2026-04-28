from __future__ import annotations

from ..entities.estimation import Estimation, SimilarTask
from ..entities.task import Task
from ..ports.llm_port import LLMPort
from ..ports.task_repository_port import TaskRepositoryPort
from ..ports.vector_store_port import VectorStorePort, SearchResult


class EstimationService:
    """Coordinates historical context, RAG search and LLM to produce estimations.

    This service lives in the domain and only depends on ports — no concrete adapters.
    """

    def __init__(
        self,
        llm_port: LLMPort,
        task_repo: TaskRepositoryPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._llm = llm_port
        self._task_repo = task_repo
        self._vector_store = vector_store

    async def estimate(self, task: Task, similar_chunks: list[SearchResult]) -> Estimation:
        # TODO: implement
        # 1. Build prompt with task description + similar historical tasks from similar_chunks
        # 2. Call self._llm.complete() with json_mode=True
        # 3. Parse and validate LLM output against Fibonacci scale
        # 4. Return Estimation entity
        raise NotImplementedError

    async def breakdown_epic(self, epic: Task) -> list[Task]:
        # TODO: implement
        # 1. Call LLM to decompose epic into user stories (max 15)
        # 2. Return list of Task stubs (status=BACKLOG, no points yet)
        raise NotImplementedError
