from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Returns embedding vector for a single text."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Returns embedding vectors for a batch of texts."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the vector dimensionality of the embedding model."""
        ...
