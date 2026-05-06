from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.adapters.primary.api.auth_router import get_login_use_case, require_auth
from src.adapters.secondary.auth.jwt_auth_adapter import JWTAuthAdapter
from src.application.use_cases.login_use_case import LoginUseCase, TokenResult
from src.domain.exceptions import InvalidCredentialsError
from src.infrastructure.main import app

SECRET = "test-secret"
USER_ID = uuid.uuid4()
EMAIL = "user@example.com"

_jwt = JWTAuthAdapter(secret=SECRET)


def _valid_token() -> str:
    return _jwt.create_access_token(USER_ID, EMAIL)


def _mock_login_use_case(result: TokenResult | None = None, *, raises: bool = False) -> LoginUseCase:
    uc = AsyncMock(spec=LoginUseCase)
    if raises:
        uc.execute.side_effect = InvalidCredentialsError()
    else:
        uc.execute.return_value = result or TokenResult(
            access_token="acc", refresh_token="ref", expires_in=3600
        )
    return uc


class TestLogin:
    def test_valid_credentials_return_200_with_tokens(self) -> None:
        result = TokenResult(access_token="acc", refresh_token="ref", expires_in=3600)
        app.dependency_overrides[get_login_use_case] = lambda: _mock_login_use_case(result)
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": "pass"})
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "acc"
        assert data["refresh_token"] == "ref"
        assert data["expires_in"] == 3600
        assert data["token_type"] == "bearer"

    def test_invalid_credentials_return_401(self) -> None:
        app.dependency_overrides[get_login_use_case] = lambda: _mock_login_use_case(raises=True)
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": "wrong"})
        app.dependency_overrides.clear()

        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials"

    def test_missing_fields_return_422(self) -> None:
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={"email": EMAIL})
        assert resp.status_code == 422


class TestRefresh:
    def test_valid_refresh_token_returns_new_tokens(self) -> None:
        refresh_token = _jwt.create_refresh_token(USER_ID, EMAIL)
        with MagicMock() as mock_container:
            from unittest.mock import patch
            with patch("src.adapters.primary.api.auth_router.container") as mock_c:
                mock_c.jwt_auth = _jwt
                client = TestClient(app)
                resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_access_token_as_refresh_returns_401(self) -> None:
        access_token = _jwt.create_access_token(USER_ID, EMAIL)
        with MagicMock():
            from unittest.mock import patch
            with patch("src.adapters.primary.api.auth_router.container") as mock_c:
                mock_c.jwt_auth = _jwt
                client = TestClient(app)
                resp = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})

        assert resp.status_code == 401

    def test_malformed_refresh_token_returns_401(self) -> None:
        with MagicMock():
            from unittest.mock import patch
            with patch("src.adapters.primary.api.auth_router.container") as mock_c:
                mock_c.jwt_auth = _jwt
                client = TestClient(app)
                resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "bad.token"})

        assert resp.status_code == 401


class TestRequireAuth:
    def test_no_token_returns_401(self) -> None:
        app.dependency_overrides[require_auth] = None  # clear any override
        app.dependency_overrides.pop(require_auth, None)
        client = TestClient(app)
        resp = client.get("/api/v1/projects")
        assert resp.status_code == 401

    def test_valid_token_passes_through(self) -> None:
        from src.adapters.primary.api.projects_router import get_project_repo
        from src.domain.ports.project_repository_port import ProjectRepositoryPort

        repo = AsyncMock(spec=ProjectRepositoryPort)
        repo.list_all.return_value = []
        app.dependency_overrides[get_project_repo] = lambda: repo
        app.dependency_overrides[require_auth] = lambda: {"sub": str(USER_ID), "email": EMAIL}
        client = TestClient(app)
        resp = client.get("/api/v1/projects")
        app.dependency_overrides.clear()

        assert resp.status_code == 200

    def test_expired_token_returns_401_with_message(self) -> None:
        from unittest.mock import patch
        from src.domain.exceptions import TokenExpiredError

        with patch("src.adapters.primary.api.auth_router.container") as mock_c:
            mock_c.jwt_auth.decode_token.side_effect = TokenExpiredError()
            client = TestClient(app)
            resp = client.get(
                "/api/v1/projects",
                headers={"Authorization": "Bearer sometoken"},
            )

        assert resp.status_code == 401
        assert resp.json()["detail"] == "token_expired"
