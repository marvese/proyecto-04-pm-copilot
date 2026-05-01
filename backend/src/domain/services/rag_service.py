from __future__ import annotations

import asyncio

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
        embedding = await self._embedding.embed(chunk.content)
        chunk.embedding = embedding
        await self._vector_store.upsert(
            id=str(chunk.id),
            embedding=embedding,
            content=chunk.content,
            metadata={
                "project_id": str(chunk.project_id),
                "source": chunk.source.value,
                "document_id": chunk.document_id,
                "section": chunk.section or "",
                "url": chunk.url or "",
            },
            collection=KNOWLEDGE_COLLECTION,
        )

    async def index_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        await asyncio.gather(*[self.index_chunk(c) for c in chunks])

    async def search(self, query: str, project_id: str, top_k: int = 5) -> list[SearchResult]:
        query_embedding = await self._embedding.embed(query)
        return await self._vector_store.search(
            query_embedding=query_embedding,
            collection=KNOWLEDGE_COLLECTION,
            top_k=top_k,
            filter={"project_id": project_id},
        )
