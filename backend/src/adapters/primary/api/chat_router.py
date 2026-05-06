from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....domain.entities.chat import ChatMessage, ChatSession
from ....domain.ports.chat_repository_port import ChatRepositoryPort
from ....infrastructure.container import container

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class CreateSessionRequest(BaseModel):
    project_id: uuid.UUID


class SessionResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime


class SendMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    message_id: uuid.UUID
    stream_url: str


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    created_at: datetime


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_chat_repo() -> ChatRepositoryPort:
    return container.chat_repo


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    body: CreateSessionRequest,
    repo: Annotated[ChatRepositoryPort, Depends(get_chat_repo)],
) -> SessionResponse:
    session = await repo.create_session(
        ChatSession(id=uuid.uuid4(), project_id=body.project_id)
    )
    return SessionResponse(id=session.id, project_id=session.project_id, created_at=session.created_at)


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    repo: Annotated[ChatRepositoryPort, Depends(get_chat_repo)],
    project_id: Optional[uuid.UUID] = None,
) -> list[SessionResponse]:
    sessions = await repo.list_sessions(project_id=project_id)
    return [SessionResponse(id=s.id, project_id=s.project_id, created_at=s.created_at) for s in sessions]


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: uuid.UUID,
    body: SendMessageRequest,
    repo: Annotated[ChatRepositoryPort, Depends(get_chat_repo)],
) -> MessageResponse:
    session = await repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    message_id = uuid.uuid4()
    await repo.save_message(
        ChatMessage(
            id=message_id,
            session_id=session_id,
            role="user",
            content=body.content,
        )
    )
    return MessageResponse(
        message_id=message_id,
        stream_url=f"/api/v1/chat/stream/{message_id}",
    )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_session_messages(
    session_id: uuid.UUID,
    repo: Annotated[ChatRepositoryPort, Depends(get_chat_repo)],
) -> list[ChatMessageResponse]:
    session = await repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await repo.list_messages(session_id)
    return [
        ChatMessageResponse(
            id=m.id, session_id=m.session_id,
            role=m.role, content=m.content, created_at=m.created_at,
        )
        for m in messages
    ]
