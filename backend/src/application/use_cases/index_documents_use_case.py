from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Optional

from ...domain.entities.knowledge import KnowledgeChunk, KnowledgeSource
from ...domain.ports.confluence_port import ConfluencePort
from ...domain.ports.github_port import GitHubPort
from ...domain.ports.jira_port import JiraPort
from ...domain.services.chunker import DocumentChunker
from ...domain.services.rag_service import RAGService

logger = logging.getLogger(__name__)


@dataclass
class IndexDocumentsCommand:
    project_id: uuid.UUID
    sources: list[KnowledgeSource]
    force_reindex: bool = False
    confluence_space_key: Optional[str] = None
    github_repo: Optional[str] = None
    jira_project_key: Optional[str] = None


@dataclass
class IndexDocumentsResult:
    indexed_count: int
    failed_count: int
    sources_processed: list[KnowledgeSource]


class IndexDocumentsUseCase:
    def __init__(
        self,
        rag_service: RAGService,
        confluence_port: Optional[ConfluencePort],
        jira_port: Optional[JiraPort],
        github_port: Optional[GitHubPort],
        chunker: Optional[DocumentChunker] = None,
    ) -> None:
        self._rag = rag_service
        self._confluence = confluence_port
        self._jira = jira_port
        self._github = github_port
        self._chunker = chunker if chunker is not None else DocumentChunker()

    async def execute(self, command: IndexDocumentsCommand) -> IndexDocumentsResult:
        indexed = 0
        failed = 0
        processed: list[KnowledgeSource] = []

        for source in command.sources:
            try:
                chunks = await self._fetch_and_chunk(command, source)
                if chunks:
                    await self._rag.index_chunks(chunks)
                    indexed += len(chunks)
                    processed.append(source)
            except Exception as exc:
                logger.warning("Failed to index source %s: %s", source.value, exc)
                failed += 1

        return IndexDocumentsResult(
            indexed_count=indexed,
            failed_count=failed,
            sources_processed=processed,
        )

    async def _fetch_and_chunk(
        self, command: IndexDocumentsCommand, source: KnowledgeSource
    ) -> list[KnowledgeChunk]:
        if source == KnowledgeSource.CONFLUENCE:
            return await self._index_confluence(command)
        if source == KnowledgeSource.JIRA:
            return await self._index_jira(command)
        if source == KnowledgeSource.GITHUB:
            return await self._index_github(command)
        return []

    async def _index_confluence(self, command: IndexDocumentsCommand) -> list[KnowledgeChunk]:
        if not self._confluence or not command.confluence_space_key:
            return []
        pages = await self._confluence.list_pages(command.confluence_space_key)
        chunks: list[KnowledgeChunk] = []
        for page in pages:
            page_id = page.get("id", "")
            title = page.get("title", page_id)
            url = page.get("_links", {}).get("webui", "")
            try:
                content = await self._confluence.get_page_content(page_id)
                chunks.extend(self._chunker.chunk_plain_text(
                    content=content,
                    source=KnowledgeSource.CONFLUENCE,
                    document_id=page_id,
                    project_id=command.project_id,
                    url=url,
                ))
            except Exception as exc:
                logger.warning("Skipping Confluence page %s (%s): %s", page_id, title, exc)
        return chunks

    async def _index_jira(self, command: IndexDocumentsCommand) -> list[KnowledgeChunk]:
        if not self._jira or not command.jira_project_key:
            return []
        issues = await self._jira.list_issues(project_key=command.jira_project_key)
        chunks: list[KnowledgeChunk] = []
        for issue in issues:
            issue_key = issue.get("key", "")
            summary = issue.get("fields", {}).get("summary", "")
            description = issue.get("fields", {}).get("description") or ""
            content = f"{summary}\n\n{description}".strip()
            if content:
                chunks.extend(self._chunker.chunk_plain_text(
                    content=content,
                    source=KnowledgeSource.JIRA,
                    document_id=issue_key,
                    project_id=command.project_id,
                ))
        return chunks

    async def _index_github(self, command: IndexDocumentsCommand) -> list[KnowledgeChunk]:
        if not self._github or not command.github_repo:
            return []
        chunks: list[KnowledgeChunk] = []
        for path in ("README.md", "docs/ARCHITECTURE.md", "docs/PRD.md"):
            try:
                content = await self._github.get_file_content(command.github_repo, path)
                chunks.extend(self._chunker.chunk_markdown(
                    content=content,
                    source=KnowledgeSource.GITHUB,
                    document_id=path,
                    project_id=command.project_id,
                ))
            except Exception as exc:
                logger.debug("Skipping GitHub file %s: %s", path, exc)
        return chunks
