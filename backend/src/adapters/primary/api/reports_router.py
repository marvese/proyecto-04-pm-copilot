from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel

from ....domain.entities.report import ReportFormat, ReportType

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


class SprintReportRequest(BaseModel):
    project_id: uuid.UUID
    sprint_id: Optional[uuid.UUID] = None
    format: ReportFormat = ReportFormat.MARKDOWN


class StatusReportRequest(BaseModel):
    project_id: uuid.UUID
    format: ReportFormat = ReportFormat.MARKDOWN


class MeetingNotesRequest(BaseModel):
    project_id: uuid.UUID
    raw_notes: str
    format: ReportFormat = ReportFormat.MARKDOWN


class ReportResponse(BaseModel):
    id: uuid.UUID
    type: ReportType
    title: str
    content: str
    confluence_page_id: Optional[str]


@router.post("/sprint", response_model=ReportResponse)
async def sprint_report(body: SprintReportRequest) -> ReportResponse:
    # TODO: implement
    raise NotImplementedError


@router.post("/status", response_model=ReportResponse)
async def status_report(body: StatusReportRequest) -> ReportResponse:
    # TODO: implement
    raise NotImplementedError


@router.post("/meeting-notes", response_model=ReportResponse)
async def meeting_notes(body: MeetingNotesRequest) -> ReportResponse:
    # TODO: implement
    raise NotImplementedError


@router.get("/{report_id}/download/{format}")
async def download_report(report_id: uuid.UUID, format: ReportFormat) -> Response:
    # TODO: implement — returns binary file (DOCX) or redirect to Confluence
    raise NotImplementedError
