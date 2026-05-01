from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.index_documents_use_case import (
    IndexDocumentsUseCase,
    IndexDocumentsCommand,
)
from src.domain.entities.knowledge import KnowledgeChunk, KnowledgeSource
from src.domain.services.chunker import DocumentChunker
from src.domain.services.rag_service import RAGService

PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def make_chunk(source: KnowledgeSource = KnowledgeSource.CONFLUENCE) -> KnowledgeChunk:
    return KnowledgeChunk(
        id=uuid.uuid4(),
        project_id=PROJECT_ID,
        source=source,
        document_id="doc-1",
        section=None,
        content="some content",
        url=None,
    )


def make_use_case(
    confluence_pages: list[dict] | None = None,
    page_content: str = "page body",
    jira_issues: list[dict] | None = None,
    github_content: str = "readme",
) -> tuple[IndexDocumentsUseCase, AsyncMock, AsyncMock, AsyncMock, MagicMock]:
    rag = AsyncMock(spec=RAGService)
    rag.index_chunks = AsyncMock()

    confluence = AsyncMock()
    confluence.list_pages.return_value = confluence_pages or []
    confluence.get_page_content.return_value = page_content

    jira = AsyncMock()
    jira.list_issues.return_value = jira_issues or []

    github = AsyncMock()
    github.get_file_content.return_value = github_content

    chunker = MagicMock(spec=DocumentChunker)
    chunker.chunk_plain_text.return_value = [make_chunk()]
    chunker.chunk_markdown.return_value = [make_chunk()]

    uc = IndexDocumentsUseCase(
        rag_service=rag,
        confluence_port=confluence,
        jira_port=jira,
        github_port=github,
        chunker=chunker,
    )
    return uc, rag, confluence, jira, github


class TestConfluenceIndexing:
    async def test_indexes_confluence_pages(self) -> None:
        pages = [{"id": "p1", "title": "Page 1", "_links": {"webui": "http://x.com"}}]
        uc, rag, confluence, _, _ = make_use_case(confluence_pages=pages)
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.CONFLUENCE],
            confluence_space_key="TEST",
        )
        result = await uc.execute(cmd)

        confluence.list_pages.assert_awaited_once_with("TEST")
        confluence.get_page_content.assert_awaited_once_with("p1")
        rag.index_chunks.assert_awaited_once()
        assert result.indexed_count == 1
        assert KnowledgeSource.CONFLUENCE in result.sources_processed

    async def test_skips_confluence_when_no_space_key(self) -> None:
        uc, rag, confluence, _, _ = make_use_case()
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.CONFLUENCE],
            confluence_space_key=None,
        )
        result = await uc.execute(cmd)

        confluence.list_pages.assert_not_awaited()
        rag.index_chunks.assert_not_awaited()
        assert result.indexed_count == 0

    async def test_skips_confluence_when_port_is_none(self) -> None:
        rag = AsyncMock(spec=RAGService)
        chunker = MagicMock(spec=DocumentChunker)
        uc = IndexDocumentsUseCase(
            rag_service=rag,
            confluence_port=None,
            jira_port=None,
            github_port=None,
            chunker=chunker,
        )
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.CONFLUENCE],
            confluence_space_key="TEST",
        )
        result = await uc.execute(cmd)
        assert result.indexed_count == 0

    async def test_page_fetch_error_is_skipped(self) -> None:
        pages = [{"id": "p1", "title": "p1"}, {"id": "p2", "title": "p2"}]
        uc, rag, confluence, _, _ = make_use_case(confluence_pages=pages)
        # First page raises, second succeeds
        confluence.get_page_content.side_effect = [RuntimeError("fetch failed"), "ok content"]
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.CONFLUENCE],
            confluence_space_key="TEST",
        )
        result = await uc.execute(cmd)
        # One page failed, one succeeded — source still processed
        assert result.indexed_count == 1
        assert KnowledgeSource.CONFLUENCE in result.sources_processed


class TestJiraIndexing:
    async def test_indexes_jira_issues(self) -> None:
        issues = [
            {"key": "PMCP-1", "fields": {"summary": "Build feature", "description": "Details here"}},
        ]
        uc, rag, _, jira, _ = make_use_case(jira_issues=issues)
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.JIRA],
            jira_project_key="PMCP",
        )
        result = await uc.execute(cmd)

        jira.list_issues.assert_awaited_once_with(project_key="PMCP")
        rag.index_chunks.assert_awaited_once()
        assert result.indexed_count == 1

    async def test_skips_jira_when_no_project_key(self) -> None:
        uc, rag, _, jira, _ = make_use_case()
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.JIRA],
            jira_project_key=None,
        )
        result = await uc.execute(cmd)
        jira.list_issues.assert_not_awaited()
        assert result.indexed_count == 0


class TestGitHubIndexing:
    async def test_indexes_github_files(self) -> None:
        uc, rag, _, _, github = make_use_case(github_content="# README\nsome content")
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.GITHUB],
            github_repo="owner/repo",
        )
        result = await uc.execute(cmd)

        assert github.get_file_content.await_count >= 1
        assert result.indexed_count >= 1
        assert KnowledgeSource.GITHUB in result.sources_processed

    async def test_missing_github_file_is_skipped(self) -> None:
        uc, rag, _, _, github = make_use_case()
        github.get_file_content.side_effect = FileNotFoundError("not found")
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.GITHUB],
            github_repo="owner/repo",
        )
        result = await uc.execute(cmd)
        # All files missing → source processed but 0 chunks
        assert result.failed_count == 0  # per-file errors are silently skipped in github
        assert result.indexed_count == 0


class TestMultipleSources:
    async def test_processes_multiple_sources(self) -> None:
        pages = [{"id": "p1", "title": "t", "_links": {}}]
        issues = [{"key": "J-1", "fields": {"summary": "s", "description": "d"}}]
        uc, rag, _, _, _ = make_use_case(confluence_pages=pages, jira_issues=issues)
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.CONFLUENCE, KnowledgeSource.JIRA],
            confluence_space_key="SP",
            jira_project_key="PMCP",
        )
        result = await uc.execute(cmd)

        assert result.indexed_count == 2
        assert rag.index_chunks.await_count == 2

    async def test_source_failure_increments_failed_count(self) -> None:
        uc, rag, confluence, _, _ = make_use_case(
            confluence_pages=[{"id": "p1", "title": "t"}]
        )
        rag.index_chunks.side_effect = RuntimeError("vector store down")
        cmd = IndexDocumentsCommand(
            project_id=PROJECT_ID,
            sources=[KnowledgeSource.CONFLUENCE],
            confluence_space_key="SP",
        )
        result = await uc.execute(cmd)

        assert result.failed_count == 1
        assert result.indexed_count == 0
        assert result.sources_processed == []
