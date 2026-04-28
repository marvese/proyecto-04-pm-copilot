from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional


class JiraPort(ABC):
    @abstractmethod
    async def get_issue(self, jira_key: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def create_issue(self, project_key: str, fields: dict[str, Any]) -> str:
        """Creates an issue and returns the Jira key (e.g. 'PROJ-42')."""
        ...

    @abstractmethod
    async def update_issue(self, jira_key: str, fields: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def list_issues(
        self,
        project_key: str,
        jql_filter: Optional[str] = None,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
