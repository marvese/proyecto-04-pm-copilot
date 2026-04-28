from __future__ import annotations

from typing import Any, Optional

import httpx

from ....domain.ports.jira_port import JiraPort


class JiraAdapter(JiraPort):
    """Implements JiraPort using the Atlassian Jira REST API v3.

    All calls are wrapped in a circuit breaker (tenacity) at the infrastructure layer.
    """

    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth = (email, api_token)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=f"{self._base_url}/rest/api/3",
            auth=self._auth,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    async def get_issue(self, jira_key: str) -> dict[str, Any]:
        # TODO: implement — GET /issue/{issueIdOrKey}
        raise NotImplementedError

    async def create_issue(self, project_key: str, fields: dict[str, Any]) -> str:
        # TODO: implement — POST /issue
        raise NotImplementedError

    async def update_issue(self, jira_key: str, fields: dict[str, Any]) -> None:
        # TODO: implement — PUT /issue/{issueIdOrKey}
        raise NotImplementedError

    async def list_issues(
        self,
        project_key: str,
        jql_filter: Optional[str] = None,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        # TODO: implement — POST /search with JQL
        raise NotImplementedError

    async def health_check(self) -> bool:
        # TODO: implement — GET /myself
        raise NotImplementedError
