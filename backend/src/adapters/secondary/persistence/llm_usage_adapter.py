from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import LLMUsageORM

logger = logging.getLogger(__name__)

# Estimated cost per 1M tokens (input, output) in USD
_COST_TABLE: dict[str, tuple[float, float]] = {
    "claude-sonnet-4-6":          (3.00,  15.00),
    "claude-haiku-4-5-20251001":  (0.25,   1.25),
    "llama3-8b-8192":             (0.05,   0.08),   # Groq
    "mixtral-8x7b-32768":         (0.24,   0.24),   # Groq
    "gemini-1.5-flash":           (0.075,  0.30),
    "gemini-1.5-pro":             (1.25,   5.00),
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    rates = _COST_TABLE.get(model)
    if rates is None:
        return None
    in_cost, out_cost = rates
    return round((input_tokens * in_cost + output_tokens * out_cost) / 1_000_000, 6)


class LLMUsageAdapter:
    """Fire-and-forget persistence of LLM call metrics."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session_factory

    async def log(
        self,
        *,
        provider: str,
        model: str,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int | None = None,
    ) -> None:
        try:
            async with self._factory() as db:
                row = LLMUsageORM(
                    id=uuid.uuid4(),
                    provider=provider,
                    model=model,
                    task_type=task_type,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=_estimate_cost(model, input_tokens, output_tokens),
                    duration_ms=duration_ms,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(row)
                await db.commit()
        except Exception as exc:
            logger.warning("llm_usage log failed (non-critical): %s", exc)
