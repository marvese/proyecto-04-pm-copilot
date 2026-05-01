from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from ..entities.knowledge import KnowledgeChunk, KnowledgeSource

CHUNK_SIZE = 512       # approximate token limit (word-count proxy)
CHUNK_OVERLAP = 50     # overlap between consecutive chunks in words


def _split_with_overlap(words: list[str], size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += size - overlap
    return chunks


class DocumentChunker:
    """Splits documents into KnowledgeChunks suitable for embedding.

    Strategy:
    - Markdown: split by ## / ### headings; oversized sections re-split with overlap.
    - Plain text: fixed-size chunks with overlap.
    """

    def _make_chunk(
        self,
        content: str,
        source: KnowledgeSource,
        document_id: str,
        project_id: uuid.UUID,
        section: Optional[str] = None,
        url: Optional[str] = None,
        last_updated: Optional[datetime] = None,
    ) -> KnowledgeChunk:
        return KnowledgeChunk(
            id=uuid.uuid4(),
            project_id=project_id,
            source=source,
            document_id=document_id,
            section=section,
            content=content.strip(),
            url=url,
            last_updated=last_updated or datetime.utcnow(),
        )

    def _split_section(
        self,
        text: str,
        heading: Optional[str],
        source: KnowledgeSource,
        document_id: str,
        project_id: uuid.UUID,
        url: Optional[str],
        last_updated: Optional[datetime],
    ) -> list[KnowledgeChunk]:
        if len(text.split()) <= CHUNK_SIZE:
            return [self._make_chunk(text, source, document_id, project_id, heading, url, last_updated)]
        parts = _split_with_overlap(text.split(), CHUNK_SIZE, CHUNK_OVERLAP)
        return [
            self._make_chunk(p, source, document_id, project_id, heading, url, last_updated)
            for p in parts
        ]

    def chunk_markdown(
        self,
        content: str,
        source: KnowledgeSource,
        document_id: str,
        project_id: uuid.UUID,
        url: str | None = None,
        last_updated: datetime | None = None,
    ) -> list[KnowledgeChunk]:
        parts = re.split(r"(?m)^(#{2,3} .+)$", content)

        chunks: list[KnowledgeChunk] = []
        current_heading: Optional[str] = None
        current_body = ""

        for part in parts:
            if re.match(r"^#{2,3} ", part):
                if current_body.strip():
                    chunks.extend(self._split_section(
                        current_body, current_heading,
                        source, document_id, project_id, url, last_updated,
                    ))
                current_heading = part.strip()
                current_body = part + "\n"
            else:
                current_body += part

        if current_body.strip():
            chunks.extend(self._split_section(
                current_body, current_heading,
                source, document_id, project_id, url, last_updated,
            ))

        if not chunks:
            return self.chunk_plain_text(content, source, document_id, project_id, url, last_updated)

        return chunks

    def chunk_plain_text(
        self,
        content: str,
        source: KnowledgeSource,
        document_id: str,
        project_id: uuid.UUID,
        url: str | None = None,
        last_updated: datetime | None = None,
    ) -> list[KnowledgeChunk]:
        words = content.split()
        if not words:
            return []
        return [
            self._make_chunk(p, source, document_id, project_id, None, url, last_updated)
            for p in _split_with_overlap(words, CHUNK_SIZE, CHUNK_OVERLAP)
        ]
