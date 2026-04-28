from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class ConfluencePort(ABC):
    @abstractmethod
    async def get_page(self, page_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def create_page(
        self,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None,
    ) -> str:
        """Creates a page and returns its page_id."""
        ...

    @abstractmethod
    async def update_page(
        self, page_id: str, title: str, content: str, version: int
    ) -> None:
        ...

    @abstractmethod
    async def list_pages(
        self, space_key: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_page_content(self, page_id: str) -> str:
        """Returns the page body as storage format (HTML/XHTML)."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
