from __future__ import annotations

import re
import uuid
from datetime import datetime

from ...domain.entities.knowledge import KnowledgeChunk, KnowledgeSource

CHUNK_SIZE = 512       # tokens (approximate — use word count as proxy before tokenizer)
CHUNK_OVERLAP = 50     # tokens overlap between consecutive chunks


class DocumentChunker:
    """Splits documents into KnowledgeChunks suitable for embedding.

    Strategy (per FUNCTIONAL_SPEC §5.2):
    - Split by Markdown sections (##, ###) when possible
    - Fall back to fixed-size chunks with overlap
    """

    def chunk_markdown(
        self,
        content: str,
        source: KnowledgeSource,
        document_id: str,
        project_id: uuid.UUID,
        url: str | None = None,
        last_updated: datetime | None = None,
    ) -> list[KnowledgeChunk]:
        # TODO: implement
        # 1. Split by Markdown headings (## / ###)
        # 2. If any section exceeds CHUNK_SIZE words, split further with overlap
        # 3. Return list of KnowledgeChunk
        raise NotImplementedError

    def chunk_plain_text(
        self,
        content: str,
        source: KnowledgeSource,
        document_id: str,
        project_id: uuid.UUID,
        url: str | None = None,
        last_updated: datetime | None = None,
    ) -> list[KnowledgeChunk]:
        # TODO: implement — fixed-size chunks with CHUNK_OVERLAP
        raise NotImplementedError
