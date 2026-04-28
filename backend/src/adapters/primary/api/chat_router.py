from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


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


class ChatMessage(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(body: CreateSessionRequest) -> SessionResponse:
    # TODO: implement
    raise NotImplementedError


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(project_id: Optional[uuid.UUID] = None) -> list[SessionResponse]:
    # TODO: implement
    raise NotImplementedError


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(session_id: uuid.UUID, body: SendMessageRequest) -> MessageResponse:
    # TODO: implement — creates pending message, returns stream_url for WebSocket
    raise NotImplementedError


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_session_messages(session_id: uuid.UUID) -> list[ChatMessage]:
    # TODO: implement
    raise NotImplementedError
