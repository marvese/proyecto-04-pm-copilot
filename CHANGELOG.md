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
- `scripts/jira_descriptions.json` — backlog completo documentado: 9 épicas + 37 historias con descripción técnica, criterios de aceptación y estimaciones (37.8h vibe coding / 127.0h senior sin IA, ratio 3.4×)
- `scripts/jira_descriptions_complete.json` — versión extendida con campo `prompt` (contexto + instrucción de implementación) para cada historia
- `scripts/update_jira.py` — actualiza descripción ADF y story points en todos los issues de Jira desde `jira_descriptions_complete.json`; soporta `--dry-run` y `--key PMCP-X`; descubrimiento automático del campo Story Points (`customfield_10032`)
- `scripts/add_task_jira.py` — crea un issue Story en Jira con descripción ADF completa (descripción, criterios de aceptación, estimaciones, prompt de implementación)
- `scripts/confluence_client.py` — cliente Confluence reutilizable para publicar páginas via REST API con conversión markdown→storage y gestión de jerarquía
- `scripts/publish_prompts.py` — publica `docs/PROMPTS.md` en el espacio Confluence `PBPMIA`, página `06. Biblioteca de Prompts`
- **Jira PMCP-47** — nueva historia bajo PMCP-6: "Tabla llm_usage y logging de consumo por llamada" (3 SP); tabla PostgreSQL para registrar consumo real de cada llamada LLM con logging fire-and-forget en `ClaudeAdapter`
- **PMCP-5**: `scripts/verify_env.py` — verifica variables `.env`, conexión PostgreSQL (SELECT 1 + 7 tablas), heartbeat ChromaDB v2, Ollama con `nomic-embed-text`; `make verify` añadido al Makefile; épica PMCP-1 completada al 100%
- **PMCP-7**: `ClaudeAdapter` implementado — `complete()` con `json_mode`, `stream()` via `messages.stream()`, `health_check()` con ping a Haiku; helper `_build_kwargs` centraliza construcción de parámetros
- **PMCP-8**: `LLMRouter` refactorizado — `retry_attempts` configurable (permite `=1` en tests para evitar backoff), `_try_providers()` separado del retry loop; routing: REASONING→Claude→Gemini→Ollama, CLASSIFICATION→Groq→Ollama→Claude
- **PMCP-9**: 14 tests unitarios del `LLMRouter` con `AsyncMock`, 98% cobertura — cubre LOCAL/HYBRID, fallback entre proveedores, streaming con fallo y recuperación, health check; sin llamadas reales a APIs
- **PMCP-10**: `OllamaLLMAdapter` implementado — `complete()` y `stream()` via `httpx` puro (POST `/api/chat`), streaming por NDJSON line-by-line, `health_check()` via GET `/api/tags`; modelo por defecto `llama3.2`

### Fixed
- **PMCP-5**: `asyncpg.connect()` requiere scheme `postgresql://`; `DATABASE_URL` de SQLAlchemy usa `postgresql+asyncpg://` — se normaliza antes de conectar
- **PMCP-5**: ChromaDB v2 depreca `/api/v1/heartbeat`; endpoint correcto es `/api/v2/heartbeat`
