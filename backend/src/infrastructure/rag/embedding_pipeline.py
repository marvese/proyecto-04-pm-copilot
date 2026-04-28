from __future__ import annotations

import logging

from ...domain.entities.knowledge import KnowledgeChunk
from ...domain.ports.embedding_port import EmbeddingPort
from ...domain.ports.vector_store_port import VectorStorePort

logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """Orchestrates batch embedding and vector store upsert for knowledge chunks."""

    def __init__(self, embedding_port: EmbeddingPort, vector_store: VectorStorePort) -> None:
        self._embedding = embedding_port
        self._vector_store = vector_store

    async def index(self, chunks: list[KnowledgeChunk], collection: str) -> tuple[int, int]:
        """Embeds and upserts chunks. Returns (success_count, failure_count)."""
        # TODO: implement
        # 1. embed_batch all chunk contents
        # 2. For each (chunk, embedding): vector_store.upsert(...)
        # 3. Return counts
        raise NotImplementedError
