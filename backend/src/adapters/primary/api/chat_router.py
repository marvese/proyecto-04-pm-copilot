from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# In-memory store — replaced by PostgreSQL adapter in PMCP-27
_sessions: dict[str, dict] = {}
_messages: dict[str, dict] = {}

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
    role: str
    content: str
    created_at: datetime


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(body: CreateSessionRequest) -> SessionResponse:
    session_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    _sessions[str(session_id)] = {
        "id": session_id,
        "project_id": body.project_id,
        "created_at": now,
    }
    return SessionResponse(id=session_id, project_id=body.project_id, created_at=now)


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(project_id: Optional[uuid.UUID] = None) -> list[SessionResponse]:
    sessions = list(_sessions.values())
    if project_id:
        sessions = [s for s in sessions if s["project_id"] == project_id]
    return [SessionResponse(**s) for s in sessions]


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(session_id: uuid.UUID, body: SendMessageRequest) -> MessageResponse:
    if str(session_id) not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    message_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    session = _sessions[str(session_id)]

    _messages[str(message_id)] = {
        "id": message_id,
        "session_id": session_id,
        "project_id": session["project_id"],
        "role": "user",
        "content": body.content,
        "created_at": now,
        "response": None,
    }
    return MessageResponse(
        message_id=message_id,
        stream_url=f"/api/v1/chat/stream/{message_id}",
    )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_session_messages(session_id: uuid.UUID) -> list[ChatMessage]:
    if str(session_id) not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = [
        m for m in _messages.values()
        if m["session_id"] == session_id
    ]
    return [
        ChatMessage(
            id=m["id"], session_id=m["session_id"],
            role=m["role"], content=m["content"], created_at=m["created_at"],
        )
        for m in msgs
    ]


def get_pending_message(message_id: uuid.UUID) -> Optional[dict]:
    return _messages.get(str(message_id))


def save_assistant_response(message_id: uuid.UUID, content: str) -> None:
    if str(message_id) in _messages:
        pending = _messages[str(message_id)]
        session_id = pending["session_id"]
        assistant_id = uuid.uuid4()
        _messages[str(assistant_id)] = {
            "id": assistant_id,
            "session_id": session_id,
            "project_id": pending["project_id"],
            "role": "assistant",
            "content": content,
            "created_at": datetime.now(timezone.utc),
            "response": None,
        }
