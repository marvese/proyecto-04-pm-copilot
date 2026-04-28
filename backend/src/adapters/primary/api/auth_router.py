from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    # TODO: implement — validate credentials, issue JWT
    raise NotImplementedError


@router.post("/refresh", response_model=LoginResponse)
async def refresh(body: RefreshRequest) -> LoginResponse:
    # TODO: implement — validate refresh token, issue new access token
    raise NotImplementedError
