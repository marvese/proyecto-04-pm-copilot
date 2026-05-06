from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ....domain.entities.chat import ChatMessage
from ....domain.ports.llm_port import LLMRequest, LLMTaskType
from ....infrastructure.container import container

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

_SYSTEM_PROMPT = (
    "You are PM Copilot, an AI assistant for software project management. "
    "Answer questions about the project using the provided context. "
    "Be concise and actionable."
)


@router.websocket("/api/v1/chat/stream/{message_id}")
async def chat_stream(websocket: WebSocket, message_id: uuid.UUID) -> None:
    """Streams LLM tokens for a pending chat message.

    Events sent to client:
        {"type": "token", "content": "<token>"}
        {"type": "done", "sources": [{"source": ..., "document_id": ..., "score": ...}]}
        {"type": "error", "detail": "<message>"}
    """
    await websocket.accept()
    try:
        chat_repo = container.chat_repo

        # 1. Look up the pending user message
        pending = await chat_repo.get_message(message_id)
        if pending is None:
            await websocket.send_json({"type": "error", "detail": "message_id not found"})
            await websocket.close()
            return

        # 2. Resolve project_id via session
        session = await chat_repo.get_session(pending.session_id)
        project_id: uuid.UUID = session.project_id if session else uuid.uuid4()

        user_content: str = pending.content

        # 3. Build RAG context via domain service
        sources: list[dict] = []
        context_text = ""
        try:
            chunks = await container.rag_service.search(
                query=user_content,
                project_id=str(project_id),
                top_k=3,
            )
            if chunks:
                context_text = "\n\n".join(
                    f"[{c.metadata.get('source', 'doc')}] {c.content[:300]}"
                    for c in chunks
                )
                sources = [
                    {
                        "source": c.metadata.get("source", ""),
                        "document_id": c.id,
                        "url": c.metadata.get("url"),
                        "score": round(c.score, 3),
                    }
                    for c in chunks
                ]
        except Exception as exc:
            logger.warning("RAG context retrieval failed: %s", exc)

        # 4. Build prompt
        prompt_parts = []
        if context_text:
            prompt_parts.append(f"Project context:\n{context_text}")
        prompt_parts.append(f"User: {user_content}")
        prompt = "\n\n".join(prompt_parts)

        request = LLMRequest(
            prompt=prompt,
            task_type=LLMTaskType.SIMPLE_QA,
            system=_SYSTEM_PROMPT,
            max_tokens=1024,
            temperature=0.5,
        )

        # 5. Stream tokens
        response_tokens: list[str] = []
        async for token in container.llm_router.stream(request):
            await websocket.send_json({"type": "token", "content": token})
            response_tokens.append(token)

        # 6. Persist assistant response
        full_response = "".join(response_tokens)
        await chat_repo.save_message(
            ChatMessage(
                id=uuid.uuid4(),
                session_id=pending.session_id,
                role="assistant",
                content=full_response,
            )
        )
        await websocket.send_json({"type": "done", "sources": sources})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", message_id)
    except Exception as exc:
        logger.error("chat_stream error: %s", exc)
        try:
            await websocket.send_json({"type": "error", "detail": str(exc)})
        except Exception as send_exc:
            logger.debug("Could not send error frame to client: %s", send_exc)
