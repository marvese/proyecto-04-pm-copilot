from __future__ import annotations

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from src.adapters.secondary.integrations.confluence_adapter import (
    ConfluenceAdapter,
    markdown_to_storage,
)


@pytest.fixture
def adapter():
    return ConfluenceAdapter(
        base_url="https://example.atlassian.net",
        email="user@example.com",
        api_token="token123",
    )


def _mock_response(status_code: int, json_data: dict) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock(
        side_effect=None if status_code < 400 else httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    )
    return resp


class TestMarkdownToStorage:
    def test_heading_conversion(self):
        result = markdown_to_storage("# Hello World")
        assert "<h1>Hello World</h1>" in result

    def test_bold_inline(self):
        result = markdown_to_storage("Text with **bold** word")
        assert "<strong>bold</strong>" in result

    def test_code_block(self):
        result = markdown_to_storage("```python\nprint('hi')\n```")
        assert 'ac:name="code"' in result
        assert "print" in result

    def test_bullet_list(self):
        result = markdown_to_storage("- item one\n- item two")
        assert "<ul>" in result
        assert "<li>item one</li>" in result

    def test_table(self):
        result = markdown_to_storage("| A | B |\n|---|---|\n| 1 | 2 |")
        assert "<table>" in result
        assert "<th>" in result


class TestConfluenceAdapterGetPage:
    @pytest.mark.asyncio
    async def test_get_page_returns_dict(self, adapter):
        payload = {"id": "123", "title": "My Page", "body": {"storage": {"value": "<p>Hi</p>"}}}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, payload))

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.get_page("123")

        assert result["id"] == "123"
        mock_client.get.assert_called_once_with(
            "content/123", params={"expand": "body.storage,version"}
        )


class TestConfluenceAdapterCreatePage:
    @pytest.mark.asyncio
    async def test_create_page_returns_id(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=_mock_response(200, {"id": "456"}))

        with patch.object(adapter, "_client", return_value=mock_client):
            page_id = await adapter.create_page("PBPMIA", "New Page", "<p>Content</p>")

        assert page_id == "456"

    @pytest.mark.asyncio
    async def test_create_page_with_parent_sends_ancestors(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=_mock_response(200, {"id": "789"}))

        with patch.object(adapter, "_client", return_value=mock_client):
            await adapter.create_page("PBPMIA", "Child Page", "<p>Hi</p>", parent_id="100")

        body = mock_client.post.call_args.kwargs["json"]
        assert body["ancestors"] == [{"id": "100"}]


class TestConfluenceAdapterUpdatePage:
    @pytest.mark.asyncio
    async def test_update_page_increments_version(self, adapter):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=resp)

        with patch.object(adapter, "_client", return_value=mock_client):
            await adapter.update_page("123", "Title", "<p>New</p>", version=5)

        body = mock_client.put.call_args.kwargs["json"]
        assert body["version"]["number"] == 6


class TestConfluenceAdapterGetPageContent:
    @pytest.mark.asyncio
    async def test_get_page_content_returns_storage_value(self, adapter):
        payload = {"body": {"storage": {"value": "<p>Hello</p>"}}}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, payload))

        with patch.object(adapter, "_client", return_value=mock_client):
            content = await adapter.get_page_content("123")

        assert content == "<p>Hello</p>"


class TestConfluenceAdapterHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_true_on_200(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, {"results": []}))

        with patch.object(adapter, "_client", return_value=mock_client):
            assert await adapter.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_false_on_exception(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(side_effect=Exception("timeout"))
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, "_client", return_value=mock_client):
            assert await adapter.health_check() is False
