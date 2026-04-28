from __future__ import annotations

from ...domain.ports.embedding_port import EmbeddingPort
from ...domain.ports.llm_port import LLMPort
from ...domain.ports.task_repository_port import TaskRepositoryPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.services.estimation_service import EstimationService
from ..commands.estimate_task_command import EstimateTaskCommand, EstimateTaskResult


class EstimateTaskUseCase:
    def __init__(
        self,
        llm_port: LLMPort,
        task_repo: TaskRepositoryPort,
        embedding_port: EmbeddingPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._estimation_service = EstimationService(llm_port, task_repo, vector_store)
        self._embedding = embedding_port
        self._vector_store = vector_store

    async def execute(self, command: EstimateTaskCommand) -> EstimateTaskResult:
        # TODO: implement
        # 1. Embed task description
        # 2. Search similar tasks in vector store (collection=project tasks)
        # 3. Call EstimationService.estimate()
        # 4. Persist estimation
        # 5. Return EstimateTaskResult
        raise NotImplementedError
