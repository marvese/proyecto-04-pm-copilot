from __future__ import annotations

from typing import Any, Optional

import httpx

from ....domain.ports.confluence_port import ConfluencePort


class ConfluenceAdapter(ConfluencePort):
    """Implements ConfluencePort using the Confluence REST API v1.

    Reuses the existing confluence_client.py pattern from scripts/.
    All calls wrapped in circuit breaker at infrastructure layer.
    """

    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth = (email, api_token)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=f"{self._base_url}/wiki/rest/api",
            auth=self._auth,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    async def get_page(self, page_id: str) -> dict[str, Any]:
        # TODO: implement — GET /content/{id}?expand=body.storage,version
        raise NotImplementedError

    async def create_page(
        self,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None,
    ) -> str:
        # TODO: implement — POST /content
        raise NotImplementedError

    async def update_page(
        self, page_id: str, title: str, content: str, version: int
    ) -> None:
        # TODO: implement — PUT /content/{id}
        raise NotImplementedError

    async def list_pages(
        self, space_key: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        # TODO: implement — GET /content?spaceKey=...&type=page
        raise NotImplementedError

    async def get_page_content(self, page_id: str) -> str:
        # TODO: implement — returns body.storage.value
        raise NotImplementedError

    async def health_check(self) -> bool:
        # TODO: implement — GET /space/{spaceKey}
        raise NotImplementedError
