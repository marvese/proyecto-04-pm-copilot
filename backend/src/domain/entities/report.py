from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ReportType(str, Enum):
    SPRINT_STATUS = "sprint_status"
    PROJECT_STATUS = "project_status"
    MEETING_NOTES = "meeting_notes"


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    DOCX = "docx"
    CONFLUENCE = "confluence"


@dataclass
class Report:
    id: uuid.UUID
    project_id: uuid.UUID
    type: ReportType
    title: str
    content: str  # Markdown
    sprint_id: Optional[uuid.UUID] = None
    confluence_page_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def export(self, format: ReportFormat) -> bytes:
        # TODO: implement — converts content to the requested format
        raise NotImplementedError
