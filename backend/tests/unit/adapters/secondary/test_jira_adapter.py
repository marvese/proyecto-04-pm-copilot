from __future__ import annotations

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from src.adapters.secondary.integrations.jira_adapter import JiraAdapter


@pytest.fixture
def adapter():
    return JiraAdapter(
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


class TestJiraAdapterGetIssue:
    @pytest.mark.asyncio
    async def test_get_issue_returns_dict(self, adapter):
        payload = {"key": "PMCP-1", "fields": {"summary": "Test"}}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, payload))

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.get_issue("PMCP-1")

        assert result["key"] == "PMCP-1"
        mock_client.get.assert_called_once_with("issue/PMCP-1")

    @pytest.mark.asyncio
    async def test_get_issue_raises_on_http_error(self, adapter):
        resp = MagicMock()
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=resp
        )
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=resp)

        with patch.object(adapter, "_client", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await adapter.get_issue("PMCP-999")


class TestJiraAdapterCreateIssue:
    @pytest.mark.asyncio
    async def test_create_issue_returns_key(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=_mock_response(201, {"key": "PMCP-42"}))

        with patch.object(adapter, "_client", return_value=mock_client):
            key = await adapter.create_issue("PMCP", {"summary": "New task", "issuetype": {"name": "Story"}})

        assert key == "PMCP-42"

    @pytest.mark.asyncio
    async def test_create_issue_sends_project_key_in_body(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=_mock_response(201, {"key": "PMCP-43"}))

        with patch.object(adapter, "_client", return_value=mock_client):
            await adapter.create_issue("PMCP", {"summary": "Task"})

        call_kwargs = mock_client.post.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs.args[1] if len(call_kwargs.args) > 1 else call_kwargs.kwargs["json"]
        assert body["fields"]["project"]["key"] == "PMCP"


class TestJiraAdapterUpdateIssue:
    @pytest.mark.asyncio
    async def test_update_issue_calls_put(self, adapter):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=resp)

        with patch.object(adapter, "_client", return_value=mock_client):
            await adapter.update_issue("PMCP-1", {"summary": "Updated"})

        mock_client.put.assert_called_once_with(
            "issue/PMCP-1", json={"fields": {"summary": "Updated"}}
        )


class TestJiraAdapterListIssues:
    @pytest.mark.asyncio
    async def test_list_issues_returns_list(self, adapter):
        issues = [{"key": "PMCP-1"}, {"key": "PMCP-2"}]
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, {"issues": issues}))

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.list_issues("PMCP")

        assert len(result) == 2
        assert result[0]["key"] == "PMCP-1"

    @pytest.mark.asyncio
    async def test_list_issues_appends_jql_filter(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, {"issues": []}))

        with patch.object(adapter, "_client", return_value=mock_client):
            await adapter.list_issues("PMCP", jql_filter="AND status=Done")

        params = mock_client.get.call_args.kwargs["params"]
        assert "AND status=Done" in params["jql"]


class TestJiraAdapterHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_returns_true_on_200(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, {}))

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_returns_false_on_exception(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(side_effect=Exception("conn refused"))
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.health_check()

        assert result is False
