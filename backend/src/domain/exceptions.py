from __future__ import annotations


class DomainError(Exception):
    """Base class for domain-level business rule violations."""


class InvalidCredentialsError(DomainError):
    """Raised when login credentials are invalid."""


class TokenExpiredError(DomainError):
    """Raised when a JWT has expired."""


class InvalidTokenError(DomainError):
    """Raised when a JWT is malformed or has an invalid signature."""
