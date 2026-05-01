from __future__ import annotations

from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ....domain.ports.vector_store_port import VectorStorePort, SearchResult

_RETRYABLE = (ConnectionError, OSError, TimeoutError)


class ChromaDBAdapter(VectorStorePort):
    """Implements VectorStorePort using ChromaDB AsyncHttpClient.

    Both local (Docker) and remote (Railway) modes supported via host/port config.
    Client is lazily initialized on first use (async context required).
    """

    def __init__(self, host: str = "localhost", port: int = 8001) -> None:
        self._host = host
        self._port = port
        self._client: Any = None

    async def _get_client(self) -> Any:
        if self._client is None:
            import chromadb  # lazy import — not needed until first call
            self._client = await chromadb.AsyncHttpClient(
                host=self._host, port=self._port
            )
        return self._client

    @retry(
        retry=retry_if_exception_type(_RETRYABLE),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def upsert(
        self,
        id: str,
        embedding: list[float],
        content: str,
        metadata: dict[str, Any],
        collection: str,
    ) -> None:
        client = await self._get_client()
        col = await client.get_or_create_collection(name=collection)
        await col.upsert(
            ids=[id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
        )

    @retry(
        retry=retry_if_exception_type(_RETRYABLE),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def search(
        self,
        query_embedding: list[float],
        collection: str,
        top_k: int = 5,
        filter: Optional[dict[str, Any]] = None,
    ) -> list[SearchResult]:
        client = await self._get_client()
        try:
            col = await client.get_collection(name=collection)
        except Exception:
            return []

        results = await col.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter if filter else None,
            include=["documents", "metadatas", "distances"],
        )

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        return [
            SearchResult(
                id=ids[i],
                content=documents[i],
                score=round(1.0 - distances[i], 4),
                metadata=metadatas[i] or {},
            )
            for i in range(len(ids))
        ]

    async def delete(self, id: str, collection: str) -> None:
        client = await self._get_client()
        try:
            col = await client.get_collection(name=collection)
            await col.delete(ids=[id])
        except Exception:
            pass

    async def collection_exists(self, collection: str) -> bool:
        client = await self._get_client()
        try:
            await client.get_collection(name=collection)
            return True
        except Exception:
            return False
