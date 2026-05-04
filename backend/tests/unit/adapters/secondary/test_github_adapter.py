from __future__ import annotations

import base64

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.adapters.secondary.integrations.github_adapter import GitHubAdapter


@pytest.fixture
def adapter():
    return GitHubAdapter(token="ghp_test_token")


def _mock_response(status_code: int, json_data) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock(
        side_effect=None if status_code < 400 else httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    )
    return resp


class TestGitHubAdapterListPullRequests:
    @pytest.mark.asyncio
    async def test_list_prs_returns_list(self, adapter):
        prs = [{"number": 1, "title": "Fix bug"}, {"number": 2, "title": "Add feature"}]
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, prs))

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.list_pull_requests("owner/repo")

        assert len(result) == 2
        assert result[0]["number"] == 1

    @pytest.mark.asyncio
    async def test_list_prs_passes_state_param(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, []))

        with patch.object(adapter, "_client", return_value=mock_client):
            await adapter.list_pull_requests("owner/repo", state="closed")

        params = mock_client.get.call_args.kwargs["params"]
        assert params["state"] == "closed"


class TestGitHubAdapterGetPullRequest:
    @pytest.mark.asyncio
    async def test_get_pr_returns_dict(self, adapter):
        pr = {"number": 42, "title": "My PR", "state": "open"}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, pr))

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.get_pull_request("owner/repo", 42)

        assert result["number"] == 42
        mock_client.get.assert_called_once_with("/repos/owner/repo/pulls/42")


class TestGitHubAdapterListIssues:
    @pytest.mark.asyncio
    async def test_list_issues_returns_list(self, adapter):
        issues = [{"number": 10, "title": "Bug report"}]
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, issues))

        with patch.object(adapter, "_client", return_value=mock_client):
            result = await adapter.list_issues("owner/repo")

        assert result[0]["number"] == 10


class TestGitHubAdapterGetFileContent:
    @pytest.mark.asyncio
    async def test_get_file_content_decodes_base64(self, adapter):
        raw = "Hello, World!\n"
        encoded = base64.b64encode(raw.encode()).decode()
        payload = {"content": encoded + "\n", "encoding": "base64"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, payload))

        with patch.object(adapter, "_client", return_value=mock_client):
            content = await adapter.get_file_content("owner/repo", "README.md")

        assert content == raw

    @pytest.mark.asyncio
    async def test_get_file_content_uses_ref(self, adapter):
        encoded = base64.b64encode(b"data").decode()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(
            return_value=_mock_response(200, {"content": encoded})
        )

        with patch.object(adapter, "_client", return_value=mock_client):
            await adapter.get_file_content("owner/repo", "file.txt", ref="develop")

        params = mock_client.get.call_args.kwargs["params"]
        assert params["ref"] == "develop"


class TestGitHubAdapterHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_true_on_200(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=_mock_response(200, {"login": "user"}))

        with patch.object(adapter, "_client", return_value=mock_client):
            assert await adapter.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_false_on_exception(self, adapter):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(side_effect=Exception("network error"))
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, "_client", return_value=mock_client):
            assert await adapter.health_check() is False
