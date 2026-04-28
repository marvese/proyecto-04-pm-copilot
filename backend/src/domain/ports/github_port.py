from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class GitHubPort(ABC):
    @abstractmethod
    async def list_pull_requests(
        self, repo: str, state: str = "open"
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_pull_request(self, repo: str, pr_number: int) -> dict[str, Any]:
        ...

    @abstractmethod
    async def list_issues(
        self, repo: str, state: str = "open"
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_file_content(self, repo: str, path: str, ref: str = "main") -> str:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
