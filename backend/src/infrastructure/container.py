from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config.settings import Settings, settings
from .llm_router.llm_router import LLMRouter
from .rag.embedding_pipeline import EmbeddingPipeline
from ..domain.services.chunker import DocumentChunker
from ..adapters.secondary.embedding.ollama_embedding_adapter import OllamaEmbeddingAdapter
from ..adapters.secondary.llm.claude_adapter import ClaudeAdapter
from ..adapters.secondary.llm.ollama_llm_adapter import OllamaLLMAdapter
from ..adapters.secondary.llm.groq_adapter import GroqAdapter
from ..adapters.secondary.llm.gemini_adapter import GeminiAdapter
from ..adapters.secondary.vector_store.chromadb_adapter import ChromaDBAdapter
from ..adapters.secondary.integrations.confluence_adapter import ConfluenceAdapter
from ..adapters.secondary.integrations.jira_adapter import JiraAdapter
from ..adapters.secondary.integrations.github_adapter import GitHubAdapter
from ..adapters.secondary.auth.jwt_auth_adapter import JWTAuthAdapter
from ..adapters.secondary.persistence.postgresql_task_adapter import PostgreSQLTaskAdapter
from ..adapters.secondary.persistence.postgresql_project_adapter import (
    PostgreSQLProjectAdapter,
    PostgreSQLSprintAdapter,
)
from ..adapters.secondary.persistence.postgresql_user_adapter import PostgreSQLUserAdapter
from ..domain.services.rag_service import RAGService
from ..application.use_cases.estimate_task_use_case import EstimateTaskUseCase
from ..application.use_cases.create_task_use_case import CreateTaskUseCase
from ..application.use_cases.query_knowledge_use_case import QueryKnowledgeUseCase
from ..application.use_cases.index_documents_use_case import IndexDocumentsUseCase
from ..application.use_cases.login_use_case import LoginUseCase
from ..application.use_cases.query_project_status_use_case import QueryProjectStatusUseCase


class Container:
    """Dependency injection container — wires adapters to use cases."""

    def __init__(self, cfg: Settings = settings) -> None:
        self._cfg = cfg
        self._llm_router: LLMRouter | None = None
        self._embedding: OllamaEmbeddingAdapter | None = None
        self._vector_store: ChromaDBAdapter | None = None
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

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
    def db_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._engine = create_async_engine(self._cfg.database_url, echo=self._cfg.debug)
            self._session_factory = async_sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )
        return self._session_factory

    @property
    def jwt_auth(self) -> JWTAuthAdapter:
        return JWTAuthAdapter(
            secret=self._cfg.secret_key,
            algorithm=self._cfg.jwt_algorithm,
            access_expire_minutes=self._cfg.jwt_access_expire_minutes,
            refresh_expire_days=self._cfg.jwt_refresh_expire_days,
        )

    @property
    def user_repo(self) -> PostgreSQLUserAdapter:
        return PostgreSQLUserAdapter(session_factory=self.db_session_factory)

    @property
    def login_use_case(self) -> LoginUseCase:
        return LoginUseCase(user_repo=self.user_repo, auth=self.jwt_auth)

    @property
    def task_repo(self) -> PostgreSQLTaskAdapter:
        return PostgreSQLTaskAdapter(session_factory=self.db_session_factory)

    @property
    def project_repo(self) -> PostgreSQLProjectAdapter:
        return PostgreSQLProjectAdapter(session_factory=self.db_session_factory)

    @property
    def sprint_repo(self) -> PostgreSQLSprintAdapter:
        return PostgreSQLSprintAdapter(session_factory=self.db_session_factory)

    @property
    def estimate_task_use_case(self) -> EstimateTaskUseCase:
        return EstimateTaskUseCase(
            llm=self.llm_router,
            embedding=self.embedding,
            vector_store=self.vector_store,
        )

    @property
    def index_documents_use_case(self) -> IndexDocumentsUseCase:
        return IndexDocumentsUseCase(
            rag_service=self.rag_service,
            confluence_port=self.confluence,
            jira_port=self.jira,
            github_port=self.github,
            chunker=DocumentChunker(),
        )

    @property
    def query_knowledge_use_case(self) -> QueryKnowledgeUseCase:
        return QueryKnowledgeUseCase(
            llm_port=self.llm_router,
            rag_service=self.rag_service,
        )

    @property
    def query_project_status_use_case(self) -> QueryProjectStatusUseCase:
        return QueryProjectStatusUseCase(
            task_repo=self.task_repo,
            sprint_repo=self.sprint_repo,
        )


container = Container()
