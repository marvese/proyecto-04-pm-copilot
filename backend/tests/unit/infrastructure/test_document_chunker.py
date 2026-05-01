from __future__ import annotations

import uuid

import pytest

from src.domain.entities.knowledge import KnowledgeSource
from src.infrastructure.rag.chunker import DocumentChunker, CHUNK_SIZE, CHUNK_OVERLAP

PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SOURCE = KnowledgeSource.CONFLUENCE
DOC_ID = "doc-1"


def chunker() -> DocumentChunker:
    return DocumentChunker()


class TestChunkMarkdown:
    def test_splits_on_headings(self) -> None:
        content = "## Section A\nContent A\n\n## Section B\nContent B"
        chunks = chunker().chunk_markdown(content, SOURCE, DOC_ID, PROJECT_ID)
        assert len(chunks) == 2
        assert "Section A" in chunks[0].content
        assert "Section B" in chunks[1].content

    def test_section_stored_as_heading(self) -> None:
        content = "## My Heading\nSome text here"
        chunks = chunker().chunk_markdown(content, SOURCE, DOC_ID, PROJECT_ID)
        assert chunks[0].section == "## My Heading"

    def test_fallback_to_plain_text_when_no_headings(self) -> None:
        content = "No headings here, just plain text that is short."
        chunks = chunker().chunk_markdown(content, SOURCE, DOC_ID, PROJECT_ID)
        assert len(chunks) == 1
        assert chunks[0].content == content.strip()

    def test_oversized_section_is_re_split(self) -> None:
        big_section = "## Big\n" + ("word " * (CHUNK_SIZE + 100))
        chunks = chunker().chunk_markdown(big_section, SOURCE, DOC_ID, PROJECT_ID)
        assert len(chunks) > 1

    def test_chunks_have_correct_project_id(self) -> None:
        content = "## A\ntext"
        chunks = chunker().chunk_markdown(content, SOURCE, DOC_ID, PROJECT_ID)
        assert all(c.project_id == PROJECT_ID for c in chunks)

    def test_url_propagated_to_chunks(self) -> None:
        content = "## A\ntext"
        chunks = chunker().chunk_markdown(content, SOURCE, DOC_ID, PROJECT_ID, url="http://example.com")
        assert all(c.url == "http://example.com" for c in chunks)


class TestChunkPlainText:
    def test_single_chunk_for_short_text(self) -> None:
        chunks = chunker().chunk_plain_text("short text", SOURCE, DOC_ID, PROJECT_ID)
        assert len(chunks) == 1
        assert chunks[0].content == "short text"

    def test_multiple_chunks_for_long_text(self) -> None:
        long_text = " ".join([f"word{i}" for i in range(CHUNK_SIZE + 100)])
        chunks = chunker().chunk_plain_text(long_text, SOURCE, DOC_ID, PROJECT_ID)
        assert len(chunks) >= 2

    def test_overlap_between_chunks(self) -> None:
        # With CHUNK_SIZE=512 and OVERLAP=50, chunk 2 starts 462 words into chunk 1
        words = [f"w{i}" for i in range(CHUNK_SIZE + CHUNK_OVERLAP + 10)]
        long_text = " ".join(words)
        chunks = chunker().chunk_plain_text(long_text, SOURCE, DOC_ID, PROJECT_ID)
        # Last words of chunk 1 should appear at start of chunk 2
        last_words_chunk1 = chunks[0].content.split()[-CHUNK_OVERLAP:]
        first_words_chunk2 = chunks[1].content.split()[:CHUNK_OVERLAP]
        assert last_words_chunk1 == first_words_chunk2

    def test_empty_text_returns_no_chunks(self) -> None:
        chunks = chunker().chunk_plain_text("", SOURCE, DOC_ID, PROJECT_ID)
        assert chunks == []

    def test_section_is_none_for_plain_text(self) -> None:
        chunks = chunker().chunk_plain_text("some text", SOURCE, DOC_ID, PROJECT_ID)
        assert chunks[0].section is None
