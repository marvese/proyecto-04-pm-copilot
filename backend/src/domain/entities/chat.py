from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ChatSession:
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ChatMessage:
    id: uuid.UUID
    session_id: uuid.UUID
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
