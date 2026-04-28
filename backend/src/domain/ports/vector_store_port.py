from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    metadata: dict[str, Any]


class VectorStorePort(ABC):
    @abstractmethod
    async def upsert(
        self,
        id: str,
        embedding: list[float],
        content: str,
        metadata: dict[str, Any],
        collection: str,
    ) -> None:
        """Inserts or updates a document in the vector store."""
        ...

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        collection: str,
        top_k: int = 5,
        filter: Optional[dict[str, Any]] = None,
    ) -> list[SearchResult]:
        """Returns top-k most similar documents."""
        ...

    @abstractmethod
    async def delete(self, id: str, collection: str) -> None:
        """Removes a document from the vector store."""
        ...

    @abstractmethod
    async def collection_exists(self, collection: str) -> bool:
        """Returns True if the collection exists."""
        ...
