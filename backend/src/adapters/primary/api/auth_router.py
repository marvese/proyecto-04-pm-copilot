from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ....application.use_cases.login_use_case import LoginUseCase, TokenResult
from ....domain.exceptions import InvalidCredentialsError, InvalidTokenError, TokenExpiredError
from ....infrastructure.container import container

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_bearer = HTTPBearer(auto_error=False)


# ── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_login_use_case() -> LoginUseCase:
    return container.login_use_case


async def require_auth(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer)],
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = container.jwt_auth.decode_token(credentials.credentials)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="token_expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid_token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="invalid_token")
    return payload


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    use_case: Annotated[LoginUseCase, Depends(get_login_use_case)],
) -> LoginResponse:
    try:
        result: TokenResult = await use_case.execute(body.email, body.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh(body: RefreshRequest) -> LoginResponse:
    try:
        payload = container.jwt_auth.decode_token(body.refresh_token)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="token_expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid_token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="invalid_token")
    user_id = uuid.UUID(payload["sub"])
    email = payload["email"]
    return LoginResponse(
        access_token=container.jwt_auth.create_access_token(user_id, email),
        refresh_token=container.jwt_auth.create_refresh_token(user_id, email),
        expires_in=3600,
    )
