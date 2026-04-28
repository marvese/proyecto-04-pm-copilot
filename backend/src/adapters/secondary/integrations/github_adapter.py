from __future__ import annotations

from typing import Any

import httpx

from ....domain.ports.github_port import GitHubPort


class GitHubAdapter(GitHubPort):
    """Implements GitHubPort using the GitHub REST API v3."""

    GITHUB_API = "https://api.github.com"

    def __init__(self, token: str) -> None:
        self._token = token

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.GITHUB_API,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    async def list_pull_requests(self, repo: str, state: str = "open") -> list[dict[str, Any]]:
        # TODO: implement — GET /repos/{repo}/pulls?state={state}
        raise NotImplementedError

    async def get_pull_request(self, repo: str, pr_number: int) -> dict[str, Any]:
        # TODO: implement — GET /repos/{repo}/pulls/{pr_number}
        raise NotImplementedError

    async def list_issues(self, repo: str, state: str = "open") -> list[dict[str, Any]]:
        # TODO: implement — GET /repos/{repo}/issues?state={state}
        raise NotImplementedError

    async def get_file_content(self, repo: str, path: str, ref: str = "main") -> str:
        # TODO: implement — GET /repos/{repo}/contents/{path}?ref={ref}
        raise NotImplementedError

    async def health_check(self) -> bool:
        # TODO: implement — GET /rate_limit
        raise NotImplementedError
