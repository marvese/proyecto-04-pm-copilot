from __future__ import annotations

import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ....domain.ports.llm_port import LLMPort

router = APIRouter(tags=["websocket"])


@router.websocket("/api/v1/chat/stream/{message_id}")
async def chat_stream(websocket: WebSocket, message_id: uuid.UUID) -> None:
    """Streams LLM tokens for a pending chat message.

    Events sent to client:
        {"type": "token", "content": "<token>"}
        {"type": "done", "sources": [...]}
        {"type": "error", "detail": "<message>"}
    """
    await websocket.accept()
    try:
        # TODO: implement
        # 1. Look up pending message by message_id
        # 2. Build RAG context
        # 3. Stream tokens via llm_port.stream()
        # 4. Send each token as {"type": "token", "content": "..."}
        # 5. On completion send {"type": "done", "sources": [...]}
        await websocket.send_json({"type": "error", "detail": "not implemented"})
    except WebSocketDisconnect:
        pass
