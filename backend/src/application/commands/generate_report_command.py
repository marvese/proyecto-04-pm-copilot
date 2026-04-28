from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from ...domain.entities.report import ReportType, ReportFormat


@dataclass
class GenerateReportCommand:
    project_id: uuid.UUID
    type: ReportType
    format: ReportFormat = ReportFormat.MARKDOWN
    sprint_id: Optional[uuid.UUID] = None
    raw_input: Optional[str] = None  # For meeting notes: the raw transcript
