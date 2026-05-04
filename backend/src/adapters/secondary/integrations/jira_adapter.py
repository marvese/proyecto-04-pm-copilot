from __future__ import annotations

from typing import Any, Optional

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ....domain.ports.jira_port import JiraPort


def _jira_retry(fn):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )(fn)


class JiraAdapter(JiraPort):
    """Implements JiraPort using the Atlassian Jira REST API v3."""

    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth = (email, api_token)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=f"{self._base_url}/rest/api/3/",
            auth=self._auth,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30.0,
        )

    @_jira_retry
    async def get_issue(self, jira_key: str) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get(f"issue/{jira_key}")
            resp.raise_for_status()
            return resp.json()

    @_jira_retry
    async def create_issue(self, project_key: str, fields: dict[str, Any]) -> str:
        body = {"fields": {"project": {"key": project_key}, **fields}}
        async with self._client() as client:
            resp = await client.post("issue", json=body)
            resp.raise_for_status()
            return resp.json()["key"]

    @_jira_retry
    async def update_issue(self, jira_key: str, fields: dict[str, Any]) -> None:
        async with self._client() as client:
            resp = await client.put(f"issue/{jira_key}", json={"fields": fields})
            resp.raise_for_status()

    @_jira_retry
    async def list_issues(
        self,
        project_key: str,
        jql_filter: Optional[str] = None,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        jql = f"project={project_key}"
        if jql_filter:
            jql += f" {jql_filter}"
        async with self._client() as client:
            resp = await client.get(
                "search",
                params={"jql": jql, "maxResults": max_results},
            )
            resp.raise_for_status()
            return resp.json().get("issues", [])

    async def health_check(self) -> bool:
        try:
            async with self._client() as client:
                resp = await client.get("myself", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False
