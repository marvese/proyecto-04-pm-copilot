from __future__ import annotations

from dataclasses import dataclass

from ...domain.exceptions import InvalidCredentialsError
from ...domain.ports.auth_port import AuthPort
from ...domain.ports.user_repository_port import UserRepositoryPort


@dataclass
class TokenResult:
    access_token: str
    refresh_token: str
    expires_in: int


class LoginUseCase:
    def __init__(self, user_repo: UserRepositoryPort, auth: AuthPort) -> None:
        self._user_repo = user_repo
        self._auth = auth

    async def execute(self, email: str, password: str) -> TokenResult:
        user = await self._user_repo.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        if not self._auth.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        return TokenResult(
            access_token=self._auth.create_access_token(user.id, user.email),
            refresh_token=self._auth.create_refresh_token(user.id, user.email),
            expires_in=3600,
        )
