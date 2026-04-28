from __future__ import annotations

import httpx

from ....domain.ports.embedding_port import EmbeddingPort

NOMIC_EMBED_MODEL = "nomic-embed-text"
NOMIC_EMBED_DIMENSION = 768


class OllamaEmbeddingAdapter(EmbeddingPort):
    """Implements EmbeddingPort using nomic-embed-text via local Ollama.

    Completely local — no external API costs for embeddings.
    """

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self._base_url = base_url
        self._model = NOMIC_EMBED_MODEL

    async def embed(self, text: str) -> list[float]:
        # TODO: implement — POST /api/embeddings {model, prompt}
        raise NotImplementedError

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # TODO: implement — call embed() sequentially or use batch endpoint if available
        raise NotImplementedError

    @property
    def dimension(self) -> int:
        return NOMIC_EMBED_DIMENSION
