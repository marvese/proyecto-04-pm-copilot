from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.adapters.primary.api.chat_router import get_chat_repo
from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.ports.chat_repository_port import ChatRepositoryPort
from src.infrastructure.main import app

PROJECT_ID = uuid.uuid4()
SESSION_ID = uuid.uuid4()
MESSAGE_ID = uuid.uuid4()
NOW = datetime.now(timezone.utc)


def _make_session() -> ChatSession:
    return ChatSession(id=SESSION_ID, project_id=PROJECT_ID, created_at=NOW)


def _make_message(role: str = "user") -> ChatMessage:
    return ChatMessage(id=MESSAGE_ID, session_id=SESSION_ID, role=role, content="Hello", created_at=NOW)


def _mock_repo(**kwargs) -> ChatRepositoryPort:
    repo = AsyncMock(spec=ChatRepositoryPort)
    repo.create_session.return_value = kwargs.get("session", _make_session())
    repo.get_session.return_value = kwargs.get("session", _make_session())
    repo.list_sessions.return_value = kwargs.get("sessions", [_make_session()])
    repo.save_message.return_value = kwargs.get("message", _make_message())
    repo.get_message.return_value = kwargs.get("message", _make_message())
    repo.list_messages.return_value = kwargs.get("messages", [_make_message()])
    return repo


@pytest.mark.usefixtures("bypass_auth")
class TestCreateSession:
    def test_returns_201_with_session(self) -> None:
        app.dependency_overrides[get_chat_repo] = lambda: _mock_repo()
        client = TestClient(app)
        resp = client.post("/api/v1/chat/sessions", json={"project_id": str(PROJECT_ID)})
        app.dependency_overrides.pop(get_chat_repo, None)

        assert resp.status_code == 201
        data = resp.json()
        assert data["project_id"] == str(PROJECT_ID)
        assert "id" in data
        assert "created_at" in data

    def test_missing_project_id_returns_422(self) -> None:
        client = TestClient(app)
        resp = client.post("/api/v1/chat/sessions", json={})
        assert resp.status_code == 422


@pytest.mark.usefixtures("bypass_auth")
class TestListSessions:
    def test_returns_list(self) -> None:
        app.dependency_overrides[get_chat_repo] = lambda: _mock_repo()
        client = TestClient(app)
        resp = client.get("/api/v1/chat/sessions")
        app.dependency_overrides.pop(get_chat_repo, None)

        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_empty_list(self) -> None:
        app.dependency_overrides[get_chat_repo] = lambda: _mock_repo(sessions=[])
        client = TestClient(app)
        resp = client.get("/api/v1/chat/sessions")
        app.dependency_overrides.pop(get_chat_repo, None)

        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.usefixtures("bypass_auth")
class TestSendMessage:
    def test_returns_message_id_and_stream_url(self) -> None:
        app.dependency_overrides[get_chat_repo] = lambda: _mock_repo()
        client = TestClient(app)
        resp = client.post(
            f"/api/v1/chat/sessions/{SESSION_ID}/messages",
            json={"content": "What is the project status?"},
        )
        app.dependency_overrides.pop(get_chat_repo, None)

        assert resp.status_code == 200
        data = resp.json()
        assert "message_id" in data
        assert data["stream_url"].startswith("/api/v1/chat/stream/")

    def test_session_not_found_returns_404(self) -> None:
        repo = _mock_repo()
        repo.get_session.return_value = None
        app.dependency_overrides[get_chat_repo] = lambda: repo
        client = TestClient(app)
        resp = client.post(
            f"/api/v1/chat/sessions/{SESSION_ID}/messages",
            json={"content": "hello"},
        )
        app.dependency_overrides.pop(get_chat_repo, None)

        assert resp.status_code == 404


@pytest.mark.usefixtures("bypass_auth")
class TestGetSessionMessages:
    def test_returns_messages(self) -> None:
        app.dependency_overrides[get_chat_repo] = lambda: _mock_repo()
        client = TestClient(app)
        resp = client.get(f"/api/v1/chat/sessions/{SESSION_ID}/messages")
        app.dependency_overrides.pop(get_chat_repo, None)

        assert resp.status_code == 200
        msgs = resp.json()
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"
        assert msgs[0]["content"] == "Hello"

    def test_session_not_found_returns_404(self) -> None:
        repo = _mock_repo()
        repo.get_session.return_value = None
        app.dependency_overrides[get_chat_repo] = lambda: repo
        client = TestClient(app)
        resp = client.get(f"/api/v1/chat/sessions/{SESSION_ID}/messages")
        app.dependency_overrides.pop(get_chat_repo, None)

        assert resp.status_code == 404
