from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from ....application.commands.generate_report_command import GenerateReportCommand
from ....application.use_cases.generate_report_use_case import GenerateReportUseCase
from ....domain.entities.report import ReportFormat, ReportType
from ....infrastructure.container import container

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class GenerateReportRequest(BaseModel):
    project_id: uuid.UUID
    report_type: ReportType
    sprint_id: Optional[uuid.UUID] = None
    raw_notes: Optional[str] = None


class SprintReportRequest(BaseModel):
    project_id: uuid.UUID
    sprint_id: Optional[uuid.UUID] = None


class StatusReportRequest(BaseModel):
    project_id: uuid.UUID


class MeetingNotesRequest(BaseModel):
    project_id: uuid.UUID
    raw_notes: str


class ReportResponse(BaseModel):
    id: uuid.UUID
    type: ReportType
    title: str
    content: str
    sprint_id: Optional[uuid.UUID] = None


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_generate_report_use_case() -> GenerateReportUseCase:
    return container.generate_report_use_case


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _run(
    command: GenerateReportCommand,
    use_case: GenerateReportUseCase,
) -> ReportResponse:
    report = await use_case.execute(command)
    return ReportResponse(
        id=report.id,
        type=report.type,
        title=report.title,
        content=report.content,
        sprint_id=report.sprint_id,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    body: GenerateReportRequest,
    use_case: Annotated[GenerateReportUseCase, Depends(get_generate_report_use_case)],
) -> ReportResponse:
    return await _run(
        GenerateReportCommand(
            project_id=body.project_id,
            type=body.report_type,
            sprint_id=body.sprint_id,
            raw_input=body.raw_notes,
        ),
        use_case,
    )


@router.post("/sprint", response_model=ReportResponse)
async def sprint_report(
    body: SprintReportRequest,
    use_case: Annotated[GenerateReportUseCase, Depends(get_generate_report_use_case)],
) -> ReportResponse:
    return await _run(
        GenerateReportCommand(
            project_id=body.project_id,
            type=ReportType.SPRINT_STATUS,
            sprint_id=body.sprint_id,
        ),
        use_case,
    )


@router.post("/status", response_model=ReportResponse)
async def status_report(
    body: StatusReportRequest,
    use_case: Annotated[GenerateReportUseCase, Depends(get_generate_report_use_case)],
) -> ReportResponse:
    return await _run(
        GenerateReportCommand(
            project_id=body.project_id,
            type=ReportType.PROJECT_STATUS,
        ),
        use_case,
    )


@router.post("/meeting-notes", response_model=ReportResponse)
async def meeting_notes(
    body: MeetingNotesRequest,
    use_case: Annotated[GenerateReportUseCase, Depends(get_generate_report_use_case)],
) -> ReportResponse:
    return await _run(
        GenerateReportCommand(
            project_id=body.project_id,
            type=ReportType.MEETING_NOTES,
            raw_input=body.raw_notes,
        ),
        use_case,
    )


@router.get("/{report_id}/download", response_class=Response)
async def download_report(report_id: uuid.UUID) -> Response:
    # Reports are ephemeral — clients download directly from the generate response content
    raise HTTPException(status_code=410, detail="Reports are ephemeral; download from the generate response.")
