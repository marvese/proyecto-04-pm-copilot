from __future__ import annotations

import time
import uuid

import pytest

from src.adapters.secondary.auth.jwt_auth_adapter import JWTAuthAdapter
from src.domain.exceptions import InvalidTokenError, TokenExpiredError

SECRET = "test-secret"


@pytest.fixture()
def adapter() -> JWTAuthAdapter:
    return JWTAuthAdapter(secret=SECRET, access_expire_minutes=60, refresh_expire_days=7)


@pytest.fixture()
def short_lived() -> JWTAuthAdapter:
    return JWTAuthAdapter(secret=SECRET, access_expire_minutes=0, refresh_expire_days=0)


USER_ID = uuid.uuid4()
EMAIL = "test@example.com"


class TestCreateAndDecodeTokens:
    def test_access_token_decodes_correctly(self, adapter: JWTAuthAdapter) -> None:
        token = adapter.create_access_token(USER_ID, EMAIL)
        payload = adapter.decode_token(token)
        assert payload["sub"] == str(USER_ID)
        assert payload["email"] == EMAIL
        assert payload["type"] == "access"

    def test_refresh_token_decodes_correctly(self, adapter: JWTAuthAdapter) -> None:
        token = adapter.create_refresh_token(USER_ID, EMAIL)
        payload = adapter.decode_token(token)
        assert payload["sub"] == str(USER_ID)
        assert payload["email"] == EMAIL
        assert payload["type"] == "refresh"

    def test_access_and_refresh_tokens_differ(self, adapter: JWTAuthAdapter) -> None:
        access = adapter.create_access_token(USER_ID, EMAIL)
        refresh = adapter.create_refresh_token(USER_ID, EMAIL)
        assert access != refresh


class TestTokenExpiry:
    def test_expired_access_token_raises(self, short_lived: JWTAuthAdapter) -> None:
        token = short_lived.create_access_token(USER_ID, EMAIL)
        time.sleep(1)
        with pytest.raises(TokenExpiredError):
            short_lived.decode_token(token)

    def test_expired_refresh_token_raises(self, short_lived: JWTAuthAdapter) -> None:
        token = short_lived.create_refresh_token(USER_ID, EMAIL)
        time.sleep(1)
        with pytest.raises(TokenExpiredError):
            short_lived.decode_token(token)


class TestInvalidTokens:
    def test_malformed_token_raises(self, adapter: JWTAuthAdapter) -> None:
        with pytest.raises(InvalidTokenError):
            adapter.decode_token("not.a.token")

    def test_wrong_secret_raises(self, adapter: JWTAuthAdapter) -> None:
        other = JWTAuthAdapter(secret="wrong-secret")
        token = other.create_access_token(USER_ID, EMAIL)
        with pytest.raises(InvalidTokenError):
            adapter.decode_token(token)

    def test_empty_string_raises(self, adapter: JWTAuthAdapter) -> None:
        with pytest.raises(InvalidTokenError):
            adapter.decode_token("")


class TestPasswordHashing:
    def test_hash_differs_from_plain(self, adapter: JWTAuthAdapter) -> None:
        hashed = adapter.hash_password("secret123")
        assert hashed != "secret123"

    def test_verify_correct_password(self, adapter: JWTAuthAdapter) -> None:
        hashed = adapter.hash_password("secret123")
        assert adapter.verify_password("secret123", hashed) is True

    def test_verify_wrong_password(self, adapter: JWTAuthAdapter) -> None:
        hashed = adapter.hash_password("secret123")
        assert adapter.verify_password("wrong", hashed) is False
