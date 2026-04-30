from __future__ import annotations

from functools import lru_cache

from .config.settings import Settings, LLMMode, settings
from .llm_router.llm_router import LLMRouter
from .rag.chunker import DocumentChunker
from .rag.embedding_pipeline import EmbeddingPipeline
from ..adapters.secondary.embedding.ollama_embedding_adapter import OllamaEmbeddingAdapter
from ..adapters.secondary.llm.claude_adapter import ClaudeAdapter
from ..adapters.secondary.llm.ollama_llm_adapter import OllamaLLMAdapter
from ..adapters.secondary.llm.groq_adapter import GroqAdapter
from ..adapters.secondary.llm.gemini_adapter import GeminiAdapter
from ..adapters.secondary.vector_store.chromadb_adapter import ChromaDBAdapter
from ..adapters.secondary.integrations.confluence_adapter import ConfluenceAdapter
from ..adapters.secondary.integrations.jira_adapter import JiraAdapter
from ..adapters.secondary.integrations.github_adapter import GitHubAdapter
from ..domain.services.rag_service import RAGService
from ..application.use_cases.estimate_task_use_case import EstimateTaskUseCase
from ..application.use_cases.create_task_use_case import CreateTaskUseCase
from ..application.use_cases.query_knowledge_use_case import QueryKnowledgeUseCase
from ..application.use_cases.index_documents_use_case import IndexDocumentsUseCase


class Container:
    """Dependency injection container — wires adapters to use cases."""

    def __init__(self, cfg: Settings = settings) -> None:
        self._cfg = cfg
        self._llm_router: LLMRouter | None = None
        self._embedding: OllamaEmbeddingAdapter | None = None
        self._vector_store: ChromaDBAdapter | None = None

    @property
    def llm_router(self) -> LLMRouter:
        if self._llm_router is None:
            claude = (
                ClaudeAdapter(api_key=self._cfg.anthropic_api_key)
                if self._cfg.anthropic_api_key
                else None
            )
            groq = (
                GroqAdapter(api_key=self._cfg.groq_api_key)
                if self._cfg.groq_api_key
                else None
            )
            gemini = (
                GeminiAdapter(api_key=self._cfg.gemini_api_key)
                if self._cfg.gemini_api_key
                else None
            )
            ollama = OllamaLLMAdapter(
                base_url=self._cfg.ollama_base_url,
                model=self._cfg.ollama_llm_model,
            )
            self._llm_router = LLMRouter(
                claude=claude, groq=groq, gemini=gemini, ollama=ollama, mode=self._cfg.llm_mode
            )
        return self._llm_router

    @property
    def embedding(self) -> OllamaEmbeddingAdapter:
        if self._embedding is None:
            self._embedding = OllamaEmbeddingAdapter(base_url=self._cfg.ollama_base_url)
        return self._embedding

    @property
    def vector_store(self) -> ChromaDBAdapter:
        if self._vector_store is None:
            self._vector_store = ChromaDBAdapter(
                host=self._cfg.chromadb_host, port=self._cfg.chromadb_port
            )
        return self._vector_store

    @property
    def rag_service(self) -> RAGService:
        return RAGService(self.embedding, self.vector_store)

    @property
    def confluence(self) -> ConfluenceAdapter | None:
        if not (self._cfg.confluence_base_url and self._cfg.confluence_email and self._cfg.confluence_api_token):
            return None
        return ConfluenceAdapter(
            base_url=self._cfg.confluence_base_url,
            email=self._cfg.confluence_email,
            api_token=self._cfg.confluence_api_token,
        )

    @property
    def jira(self) -> JiraAdapter | None:
        if not (self._cfg.jira_base_url and self._cfg.jira_email and self._cfg.jira_api_token):
            return None
        return JiraAdapter(
            base_url=self._cfg.jira_base_url,
            email=self._cfg.jira_email,
            api_token=self._cfg.jira_api_token,
        )

    @property
    def github(self) -> GitHubAdapter | None:
        if not self._cfg.github_token:
            return None
        return GitHubAdapter(token=self._cfg.github_token)

    @property
    def estimate_task_use_case(self) -> EstimateTaskUseCase:
        return EstimateTaskUseCase(
            llm=self.llm_router,
            embedding=self.embedding,
            vector_store=self.vector_store,
        )


container = Container()
