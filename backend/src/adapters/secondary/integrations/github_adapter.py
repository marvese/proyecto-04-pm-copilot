from __future__ import annotations

import base64
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ....domain.ports.github_port import GitHubPort


def _github_retry(fn):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )(fn)


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
            timeout=30.0,
        )

    @_github_retry
    async def list_pull_requests(self, repo: str, state: str = "open") -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get(f"/repos/{repo}/pulls", params={"state": state})
            resp.raise_for_status()
            return resp.json()

    @_github_retry
    async def get_pull_request(self, repo: str, pr_number: int) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get(f"/repos/{repo}/pulls/{pr_number}")
            resp.raise_for_status()
            return resp.json()

    @_github_retry
    async def list_issues(self, repo: str, state: str = "open") -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get(f"/repos/{repo}/issues", params={"state": state})
            resp.raise_for_status()
            return resp.json()

    @_github_retry
    async def get_file_content(self, repo: str, path: str, ref: str = "main") -> str:
        async with self._client() as client:
            resp = await client.get(
                f"/repos/{repo}/contents/{path}",
                params={"ref": ref},
            )
            resp.raise_for_status()
            data = resp.json()
            encoded = data.get("content", "")
            return base64.b64decode(encoded).decode("utf-8")

    async def health_check(self) -> bool:
        try:
            async with self._client() as client:
                resp = await client.get("/user", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False
