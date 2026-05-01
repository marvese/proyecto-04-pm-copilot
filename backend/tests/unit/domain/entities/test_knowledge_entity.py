from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.entities.knowledge import KnowledgeChunk, KnowledgeSource


def make_chunk(last_updated: datetime | None = None) -> KnowledgeChunk:
    return KnowledgeChunk(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        source=KnowledgeSource.CONFLUENCE,
        document_id="page-1",
        section=None,
        content="some content",
        url=None,
        last_updated=last_updated or datetime.now(timezone.utc),
    )


class TestNeedsReindex:
    def test_fresh_chunk_does_not_need_reindex(self) -> None:
        chunk = make_chunk(datetime.now(timezone.utc))
        assert chunk.needs_reindex(max_age_days=1) is False

    def test_old_chunk_needs_reindex(self) -> None:
        old = datetime.now(timezone.utc) - timedelta(days=2)
        chunk = make_chunk(old)
        assert chunk.needs_reindex(max_age_days=1) is True

    def test_exactly_at_threshold_needs_reindex(self) -> None:
        threshold = datetime.now(timezone.utc) - timedelta(days=1, hours=1)
        chunk = make_chunk(threshold)
        assert chunk.needs_reindex(max_age_days=1) is True

    def test_custom_max_age(self) -> None:
        week_old = datetime.now(timezone.utc) - timedelta(days=7, hours=1)
        chunk = make_chunk(week_old)
        assert chunk.needs_reindex(max_age_days=7) is True
        assert chunk.needs_reindex(max_age_days=8) is False

    def test_naive_datetime_handled(self) -> None:
        # naive datetime should be treated as UTC
        naive = datetime.utcnow() - timedelta(days=2)
        chunk = make_chunk(naive)
        assert chunk.needs_reindex(max_age_days=1) is True
