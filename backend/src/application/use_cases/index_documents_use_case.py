from __future__ import annotations

import uuid
from dataclasses import dataclass

from ...domain.entities.knowledge import KnowledgeSource
from ...domain.ports.confluence_port import ConfluencePort
from ...domain.ports.github_port import GitHubPort
from ...domain.ports.jira_port import JiraPort
from ...domain.services.rag_service import RAGService


@dataclass
class IndexDocumentsCommand:
    project_id: uuid.UUID
    sources: list[KnowledgeSource]
    force_reindex: bool = False


@dataclass
class IndexDocumentsResult:
    indexed_count: int
    failed_count: int
    sources_processed: list[KnowledgeSource]


class IndexDocumentsUseCase:
    def __init__(
        self,
        rag_service: RAGService,
        confluence_port: ConfluencePort,
        jira_port: JiraPort,
        github_port: GitHubPort,
    ) -> None:
        self._rag = rag_service
        self._confluence = confluence_port
        self._jira = jira_port
        self._github = github_port

    async def execute(self, command: IndexDocumentsCommand) -> IndexDocumentsResult:
        # TODO: implement
        # 1. For each source in command.sources:
        #    - Fetch documents from the corresponding port
        #    - Chunk documents (via RAGService or Chunker)
        #    - Index via rag_service.index_chunks()
        # 2. Return counts
        raise NotImplementedError
