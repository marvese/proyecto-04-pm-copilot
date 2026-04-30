from __future__ import annotations

import uuid

from ...domain.entities.task import Task, TaskType, TaskStatus, TaskPriority
from ...domain.ports.embedding_port import EmbeddingPort
from ...domain.ports.llm_port import LLMPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.services.estimation_service import EstimationService
from ..commands.estimate_task_command import EstimateTaskCommand, EstimateTaskResult

_TASKS_COLLECTION = "tasks"


class EstimateTaskUseCase:
    """Estimates story points for a task description using RAG context + LLM.

    Flow: embed description → search similar tasks → EstimationService → result.
    Does not persist — persistence is wired in PMCP-27 (PostgreSQL adapter).
    """

    def __init__(
        self,
        llm: LLMPort,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._service = EstimationService(llm)
        self._embedding = embedding
        self._vector_store = vector_store

    async def execute(self, command: EstimateTaskCommand) -> EstimateTaskResult:
        # 1. Embed title + description for similarity search
        query_text = f"{command.title} {command.description}".strip()
        query_embedding = await self._embedding.embed(query_text)

        # 2. Retrieve similar historical tasks from the vector store
        similar_chunks = await self._vector_store.search(
            query_embedding=query_embedding,
            collection=_TASKS_COLLECTION,
            top_k=5,
            filter={"project_id": str(command.project_id)},
        )

        # 3. Build a transient Task entity (not persisted yet)
        task_id = uuid.uuid4()
        task = Task(
            id=task_id,
            project_id=command.project_id,
            title=command.title,
            description=command.description,
            type=TaskType.STORY,
            status=TaskStatus.BACKLOG,
            priority=TaskPriority.MEDIUM,
        )

        # 4. Estimate via domain service
        estimation = await self._service.estimate(task, similar_chunks)

        return EstimateTaskResult(estimation=estimation, task_id=task_id)
