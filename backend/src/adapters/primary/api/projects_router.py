from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    jira_project_key: Optional[str]
    confluence_space_key: Optional[str]
    github_repo: Optional[str]


class CreateProjectRequest(BaseModel):
    name: str
    description: str
    jira_project_key: Optional[str] = None
    confluence_space_key: Optional[str] = None
    github_repo: Optional[str] = None


@router.get("", response_model=list[ProjectResponse])
async def list_projects() -> list[ProjectResponse]:
    # TODO: implement
    raise NotImplementedError


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(body: CreateProjectRequest) -> ProjectResponse:
    # TODO: implement
    raise NotImplementedError


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID) -> ProjectResponse:
    # TODO: implement
    raise NotImplementedError
