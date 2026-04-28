# Changelog

Todos los cambios notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [Unreleased]

### Added
- Estructura completa de directorios del proyecto (backend + frontend)
- **Backend — Dominio**: entidades (`Task`, `Sprint`, `Project`, `Estimation`, `Report`, `KnowledgeChunk`), 10 puertos abstractos (`LLMPort`, `EmbeddingPort`, `VectorStorePort`, `TaskRepositoryPort`, `ProjectRepositoryPort`, `SprintRepositoryPort`, `JiraPort`, `ConfluencePort`, `GitHubPort`, `DocumentGeneratorPort`), 3 domain services (`EstimationService`, `PlanningService`, `RAGService`)
- **Backend — Application**: 9 use cases stub (`EstimateTaskUseCase`, `CreateTaskUseCase`, `UpdateTaskUseCase`, `PlanSprintUseCase`, `GenerateReportUseCase`, `QueryProjectStatusUseCase`, `IndexDocumentsUseCase`, `SyncJiraUseCase`, `QueryKnowledgeUseCase`) + 4 commands/DTOs
- **Backend — Adapters primarios**: 8 FastAPI routers (auth, projects, tasks, chat, estimate, reports, knowledge, sprints) + WebSocket handler para streaming de chat
- **Backend — Adapters secundarios**: 4 adaptadores LLM (`ClaudeAdapter`, `OllamaLLMAdapter`, `GroqAdapter`, `GeminiAdapter`), `OllamaEmbeddingAdapter`, `ChromaDBAdapter`, 2 adaptadores de persistencia PostgreSQL, 3 adaptadores de integración (Jira, Confluence, GitHub)
- **Backend — Infrastructure**: `LLMRouter` con fallback automático y tenacity, `TaskClassifier`, `DocumentChunker`, `EmbeddingPipeline`, `Settings` (pydantic-settings), `Container` (DI), `main.py` (FastAPI app), `pyproject.toml`, Alembic scaffolding
- **Backend — Tests**: `conftest.py` con fixtures, tests unitarios para entidades/services/use cases, tests de integración para adaptadores e infrastructure; todos en modo `pytest.skip` hasta implementación
- **Frontend**: tipos TypeScript (`Task`, `Project`, `Sprint`, `Chat`, `Estimation`), 5 servicios API (`chatService`, `projectService`, `taskService`, `estimationService`, `reportService`), 4 hooks (`useCopilotChat`, `useProjectContext`, `useEstimation`, `useTasks`), 9 componentes React stub (Chat, Tasks, Dashboard, UI), 4 páginas, `App.tsx` con react-router, `vite.config.ts`, `tsconfig.json`, `package.json`, `manifest.json` PWA
- `scripts/setup_jira.py` — crea proyecto Jira `PMCP` (Scrum), 9 épicas y 37 historias; idempotente con búsqueda previa via `/rest/api/3/search/jql`; estrategia de vinculación épica↔historia en 3 capas (customfield_10014 → parent → Agile API)
- `docker-compose.yml` — PostgreSQL 16-alpine + ChromaDB latest + pgAdmin (profile `tools`); red interna `pmcopilot-net`; volúmenes persistentes; healthcheck `pg_isready` en PostgreSQL
- `scripts/db_init.sql` — DDL completo: 7 tablas (`projects`, `sprints`, `tasks`, `estimations`, `knowledge_chunks`, `chat_sessions`, `chat_messages`) con UUID PKs, CHECK constraints en enums, 26 índices (GIN trigram en `tasks.title` y `knowledge_chunks.content`, índice único parcial para sprint activo por proyecto), trigger `set_updated_at()`
- `Makefile` — targets: `make up/down/logs/ps/db-init/db-reset/db-shell/tools-up/tools-down/help`
- `.env.example` — actualizado con todas las variables nuevas: `POSTGRES_*`, `CHROMADB_*`, `PGADMIN_*`, `LLM_MODE`, `SECRET_KEY`, `DEBUG`
- `docs/ADR-006-infra-local.md` — decisiones de infraestructura local: Docker Compose vs bare metal, UUID vs BIGSERIAL, VARCHAR+CHECK vs CREATE TYPE, GIN trigram vs tsvector
