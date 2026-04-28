from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class KnowledgeSource(str, Enum):
    CONFLUENCE = "confluence"
    JIRA = "jira"
    GITHUB = "github"
    CONVERSATION = "conversation"


@dataclass
class KnowledgeChunk:
    id: uuid.UUID
    project_id: uuid.UUID
    source: KnowledgeSource
    document_id: str
    section: Optional[str]
    content: str
    url: Optional[str]
    embedding: Optional[list[float]] = field(default=None, repr=False)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def needs_reindex(self, max_age_days: int = 1) -> bool:
        # TODO: implement — checks if chunk is stale
        raise NotImplementedError
