from __future__ import annotations

from ..entities.knowledge import KnowledgeChunk
from ..ports.embedding_port import EmbeddingPort
from ..ports.vector_store_port import VectorStorePort, SearchResult

KNOWLEDGE_COLLECTION = "project_knowledge"


class RAGService:
    """Manages indexing and retrieval of project knowledge chunks."""

    def __init__(self, embedding_port: EmbeddingPort, vector_store: VectorStorePort) -> None:
        self._embedding = embedding_port
        self._vector_store = vector_store

    async def index_chunk(self, chunk: KnowledgeChunk) -> None:
        # TODO: implement — embed content and upsert into vector store
        raise NotImplementedError

    async def index_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        # TODO: implement — batch embed and upsert
        raise NotImplementedError

    async def search(self, query: str, project_id: str, top_k: int = 5) -> list[SearchResult]:
        # TODO: implement
        # 1. Embed query
        # 2. Search vector store filtered by project_id
        # 3. Return top_k results
        raise NotImplementedError
