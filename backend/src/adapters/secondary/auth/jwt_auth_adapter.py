from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from ....domain.exceptions import InvalidTokenError, TokenExpiredError
from ....domain.ports.auth_port import AuthPort

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"


class JWTAuthAdapter(AuthPort):
    def __init__(
        self,
        secret: str,
        algorithm: str = "HS256",
        access_expire_minutes: int = 60,
        refresh_expire_days: int = 7,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._access_expire = timedelta(minutes=access_expire_minutes)
        self._refresh_expire = timedelta(days=refresh_expire_days)

    def _encode(self, user_id: uuid.UUID, email: str, token_type: str, ttl: timedelta) -> str:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": token_type,
            "iat": now,
            "exp": now + ttl,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def create_access_token(self, user_id: uuid.UUID, email: str) -> str:
        return self._encode(user_id, email, _ACCESS_TYPE, self._access_expire)

    def create_refresh_token(self, user_id: uuid.UUID, email: str) -> str:
        return self._encode(user_id, email, _REFRESH_TYPE, self._refresh_expire)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredError("Token has expired") from exc
        except jwt.PyJWTError as exc:
            raise InvalidTokenError("Invalid token") from exc

    def hash_password(self, plain: str) -> str:
        return _pwd_context.hash(plain)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)
