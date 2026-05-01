from __future__ import annotations

import asyncio

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ....domain.ports.embedding_port import EmbeddingPort

NOMIC_EMBED_MODEL = "nomic-embed-text"
NOMIC_EMBED_DIMENSION = 768

_RETRYABLE = (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError)


class OllamaEmbeddingAdapter(EmbeddingPort):
    """Implements EmbeddingPort using nomic-embed-text via local Ollama.

    Completely local — no external API costs for embeddings.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = NOMIC_EMBED_MODEL,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    @retry(
        retry=retry_if_exception_type(_RETRYABLE),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._base_url}/api/embeddings",
                json={"model": self._model, "prompt": text},
            )
            response.raise_for_status()
            result: list[float] = response.json()["embedding"]

        if len(result) != NOMIC_EMBED_DIMENSION:
            raise ValueError(
                f"Expected embedding dimension {NOMIC_EMBED_DIMENSION}, got {len(result)}"
            )
        return result

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return list(await asyncio.gather(*[self.embed(t) for t in texts]))

    @property
    def dimension(self) -> int:
        return NOMIC_EMBED_DIMENSION
