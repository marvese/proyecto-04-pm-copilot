from __future__ import annotations

from typing import Any, Optional

from ....domain.ports.vector_store_port import VectorStorePort, SearchResult


class ChromaDBAdapter(VectorStorePort):
    """Implements VectorStorePort using ChromaDB.

    Both local (Docker) and remote (Railway) modes supported via host/port config.
    All calls wrapped in circuit breaker at the LLMRouter/infrastructure level.
    """

    def __init__(self, host: str = "localhost", port: int = 8001) -> None:
        self._host = host
        self._port = port
        self._client = None  # TODO: init chromadb.AsyncHttpClient on first use

    async def _get_client(self):  # type: ignore[return]
        # TODO: lazy-init chromadb.AsyncHttpClient(host, port)
        raise NotImplementedError

    async def upsert(
        self,
        id: str,
        embedding: list[float],
        content: str,
        metadata: dict[str, Any],
        collection: str,
    ) -> None:
        # TODO: implement — get_or_create_collection(collection).upsert(...)
        raise NotImplementedError

    async def search(
        self,
        query_embedding: list[float],
        collection: str,
        top_k: int = 5,
        filter: Optional[dict[str, Any]] = None,
    ) -> list[SearchResult]:
        # TODO: implement — collection.query(query_embeddings=[...], n_results=top_k, where=filter)
        raise NotImplementedError

    async def delete(self, id: str, collection: str) -> None:
        # TODO: implement
        raise NotImplementedError

    async def collection_exists(self, collection: str) -> bool:
        # TODO: implement
        raise NotImplementedError
