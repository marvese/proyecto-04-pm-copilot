# Biblioteca de Prompts — PM Copilot

**Versión**: 0.11  
**Fecha**: 2026-05-01  

---

## Cómo Usar Este Fichero

Este fichero es la **biblioteca de prompts** del proyecto PM Copilot. Cada prompt significativo usado durante el desarrollo debe añadirse aquí en la sección correspondiente.

### Un prompt es significativo si:
- Generó código de producción o tests
- Definió comportamientos o decisiones del sistema
- Produjo documentación del proyecto
- Podría reutilizarse en el futuro (mismo u otro proyecto)
- Produjo un resultado especialmente bueno y merece ser preservado

### Regla de trabajo (ver también CLAUDE.md)
Al terminar una sesión de desarrollo o completar una tarea importante, revisar si hay prompts nuevos que añadir. Los prompts son artefactos de trabajo tan valiosos como el código.

### Formato de cada entrada

```markdown
### [Nombre descriptivo del prompt]
**Fecha**: YYYY-MM-DD  
**Modelo**: claude-sonnet-4-6 / claude-haiku / ollama/llama3  
**Resultado**: [descripción de lo que produjo]  
**Ficheros generados/afectados**: [lista de ficheros si aplica]  

**Prompt**:
[texto completo del prompt o patrón reutilizable]

**Notas**: [observaciones, variaciones, limitaciones conocidas]
```

### Secciones disponibles

1. [Prompts de Definición de Proyecto](#1-prompts-de-definición-de-proyecto)
2. [Prompts de Arquitectura y Diseño](#2-prompts-de-arquitectura-y-diseño)
3. [Prompts de Desarrollo Backend](#3-prompts-de-desarrollo-backend)
4. [Prompts de Desarrollo Frontend](#4-prompts-de-desarrollo-frontend)
5. [Prompts de Testing](#5-prompts-de-testing)
6. [Prompts de Documentación](#6-prompts-de-documentación)
7. [Prompts de Integración](#7-prompts-de-integración)
8. [Prompts de LLM y RAG](#8-prompts-de-llm-y-rag)
9. [Patrones y Buenas Prácticas](#9-patrones-y-buenas-prácticas)

---

## 1. Prompts de Definición de Proyecto

### 1.1 Definición Completa del Proyecto y Generación de Documentación Base

**Fecha**: 2026-04-24  
**Modelo**: claude-sonnet-4-6  
**Resultado**: Generación de toda la documentación de definición del proyecto (PRD, ARCHITECTURE, ADRs, DEFINITION_OF_DONE, FUNCTIONAL_SPEC, METODOLOGIA, CLAUDE.md, PROMPTS.md)  
**Ficheros generados**:
- `CLAUDE.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ADR-001-stack.md`
- `docs/ADR-002-hexagonal.md`
- `docs/ADR-003-circuit-breaker.md`
- `docs/ADR-004-pwa-first.md`
- `docs/ADR-005-llm-router.md`
- `docs/DEFINITION_OF_DONE.md`
- `docs/FUNCTIONAL_SPEC.md`
- `docs/METODOLOGIA.md`
- `docs/PROMPTS.md`

**Prompt**:

```
Actúa como arquitecto de software senior y PM técnico. Vamos a construir un PM Copilot: un asistente inteligente con RAG que ayuda a gestionar proyectos de software. Antes de escribir código necesito que generes toda la documentación de definición del proyecto.

El sistema tendrá:

Backend Python/FastAPI con arquitectura hexagonal
RAG con ChromaDB para conocimiento del proyecto usando embeddings con nomic-embed-text via Ollama local (http://localhost:11434)
Agente conversacional con LLM Router: Claude Sonnet/Haiku para tareas complejas, Ollama/llama3 para tareas simples y repetitivas
Circuit Breaker en todas las integraciones externas
Integraciones con Confluence, Jira y GitHub via adaptadores hexagonales
Frontend React/TypeScript PWA desplegado en Vercel
Backend desplegado en Railway con PostgreSQL + ChromaDB
POC Flutter planificada como deuda técnica futura

Capacidades principales por prioridad:

Estimaciones y planificación basadas en el conocimiento del proyecto
Creación y gestión de tareas (gestor propio + Jira)
Generación de informes y documentos (MD, DOCX, XLSX)
Seguimiento y estado del proyecto

Crea estos ficheros:

docs/PRD.md
docs/ARCHITECTURE.md con diagrama ASCII de arquitectura hexagonal
docs/ADR-001-stack.md
docs/ADR-002-hexagonal.md — hexagonal vs microservicios, migración como deuda técnica
docs/ADR-003-circuit-breaker.md
docs/ADR-004-pwa-first.md — PWA React primero, Flutter POC después
docs/ADR-005-llm-router.md — capa de abstracción LLM, Ollama para desarrollo, Claude para producción, nomic-embed-text para embeddings RAG
docs/DEFINITION_OF_DONE.md — criterios adaptados a desarrollo con IA y comportamientos no deterministas
docs/FUNCTIONAL_SPEC.md
docs/METODOLOGIA.md — metodología ágil adaptada a IA: sprints 1 semana, user stories para LLMs, criterios de aceptación no deterministas
CLAUDE.md — contexto completo con stack, estructura prevista, convenciones, reglas de trabajo y skills activos
docs/PROMPTS.md — biblioteca de prompts con secciones: "Cómo usar este fichero", "Prompts de definición de proyecto" (incluye este prompt completo como primer ejemplo), "Prompts de desarrollo", "Prompts de documentación", "Patrones y buenas prácticas"

Regla importante: cada prompt significativo usado durante el desarrollo debe añadirse a docs/PROMPTS.md en la sección correspondiente. Documenta esta regla en el CLAUDE.md como parte de las reglas de trabajo.
No crees ningún fichero de código todavía. Solo documentación.
```

**Notas**: 
- Prompt de arranque de proyecto. Usar como referencia para futuros proyectos con metodología similar.
- El modelo generó todos los ficheros en paralelo aprovechando independencia entre documentos.
- La identificación de la página raíz en Confluence requirió un paso previo de exploración de la API antes de generar los scripts.

---

### 1.2 Setup Inicial de Confluence

**Fecha**: 2026-04-24  
**Modelo**: claude-sonnet-4-6  
**Resultado**: Script Python para crear estructura de páginas en Confluence  
**Ficheros generados**: `scripts/setup_confluence.py`  

**Prompt**:

```
Tengo acceso a la API de Confluence con las credenciales en el .env. Usando la API REST de Confluence, crea la siguiente estructura de páginas en el espacio PBPMIA:

Inicio (página raíz ya existe)

01. Metodología PM con IA — página vacía con introducción placeholder
02. Diario de Desarrollo — página vacía con introducción placeholder
03. Herramientas y Configuración — página vacía con introducción placeholder
04. Lecciones Aprendidas — página vacía con introducción placeholder
05. Playbook: Vibe Coding — página vacía con introducción placeholder
06. PM Copilot — Documentación Técnica — página vacía con introducción placeholder

Usa la API REST /wiki/rest/api/content con autenticación básica (email + API token). Crea un script Python scripts/setup_confluence.py que cree estas páginas. Las credenciales vienen del .env via python-dotenv.
```

**Notas**:
- La página raíz se llama "Playbook de PM con IA", no "Inicio". El script fue adaptado para encontrar automáticamente la página raíz buscando la página sin ancestros.
- El script es idempotente: verifica si la página ya existe antes de crearla.

---

## 2. Prompts de Arquitectura y Diseño

*[Añadir prompts de arquitectura aquí a medida que se desarrollen]*

---

## 3. Prompts de Desarrollo Backend

### 3.1 Script de verificación del entorno (verify_env.py)

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: `scripts/verify_env.py` con 4 grupos de checks (variables .env, PostgreSQL+tablas, ChromaDB, LLM provider), salida ✓/✗ coloreada, exit code 0/1. Target `make verify` añadido al Makefile.
**Ficheros generados/afectados**: `scripts/verify_env.py`, `Makefile`

**Prompt**:

```
Crea scripts/verify_env.py que verifica que el entorno está correctamente configurado.

Checks:
1. Variables obligatorias del .env no vacías ni con valores placeholder
2. Conexión a PostgreSQL via asyncpg ejecutando SELECT 1
3. Existencia de las 7 tablas esperadas (projects, sprints, tasks, estimations,
   knowledge_chunks, chat_sessions, chat_messages)
4. Heartbeat de ChromaDB via GET http://{CHROMADB_HOST}:{CHROMADB_PORT}/api/v2/heartbeat
5. Si LLM_MODE=local: verificar que Ollama responde en OLLAMA_BASE_URL/api/tags
   y que 'nomic-embed-text' está disponible

Imprime ✓/✗ por check con colores ANSI y sale con exit code 1 si alguno falla.
Dependencias: asyncpg, requests, python-dotenv.

Ficheros de contexto: backend/src/infrastructure/config/settings.py,
scripts/db_init.sql, docker-compose.yml
```

**Notas**:
- `asyncpg.connect()` requiere scheme `postgresql://`, no el `postgresql+asyncpg://` de SQLAlchemy — normalizar con `.replace("postgresql+asyncpg://", "postgresql://")` antes de conectar.
- ChromaDB v0.5+ depreca `/api/v1/heartbeat` (devuelve 410). El endpoint correcto es `/api/v2/heartbeat`.
- `changeme` no debe estar en la lista de placeholder markers porque es la contraseña real de desarrollo en Docker.
- 4 iteraciones: script inicial → fix asyncpg scheme → fix ChromaDB endpoint → ajuste placeholder markers.

---

### 3.2 Implementación ClaudeAdapter, LLMRouter y OllamaLLMAdapter (PMCP-6)

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: Tres módulos implementados sobre stubs existentes. LLMRouter refactorizado con `retry_attempts` configurable para testabilidad. 14 tests unitarios con 98% cobertura.
**Ficheros generados/afectados**: `backend/src/adapters/secondary/llm/claude_adapter.py`, `backend/src/adapters/secondary/llm/ollama_llm_adapter.py`, `backend/src/infrastructure/llm_router/llm_router.py`

**Prompt**:

```
Implementa los siguientes módulos de la épica PMCP-6 (LLM Core):

PMCP-7 — ClaudeAdapter en backend/src/adapters/secondary/llm/claude_adapter.py:
- Clase ClaudeAdapter(LLMPort). DEFAULT_MODEL='claude-sonnet-4-6'.
- complete(LLMRequest) -> LLMResponse: usa AsyncAnthropic.messages.create(),
  mapea content[0].text, usage.input_tokens/output_tokens, provider='anthropic'
- stream(LLMRequest) -> AsyncIterator[str]: usa messages.stream() context manager,
  yield tokens de text_stream
- health_check() -> bool: ping con max_tokens=1 a Haiku, captura excepciones
- json_mode=True: añade instrucción al system prompt para forzar JSON

PMCP-10 — OllamaLLMAdapter en backend/src/adapters/secondary/llm/ollama_llm_adapter.py:
- Solo httpx puro (sin SDK de Anthropic/OpenAI)
- complete(): POST /api/chat con stream=False, parsea message.content
- stream(): POST /api/chat con stream=True, parsea NDJSON línea a línea
- health_check(): GET /api/tags, retorna True si status 200
- Modelo por defecto: llama3.2

PMCP-8 — LLMRouter refactorizado:
- Constructor recibe retry_attempts: int = 3 para hacer testable sin sleeps
- Separar _try_providers() del loop de retry de tenacity (AsyncRetrying)
- Routing: REASONING/GENERATION_LONG → Claude → Gemini → Ollama
           CLASSIFICATION/EXTRACTION/SIMPLE_QA → Groq → Ollama → Claude
- LOCAL mode: siempre Ollama
```

**Notas**:
- El `@retry` decorator de tenacity sobre `complete()` genera sleeps reales en tests cuando todos los proveedores fallan. Pasar a `AsyncRetrying` en el cuerpo del método con `retry_attempts` configurable resuelve esto.
- `ClaudeAdapter._build_kwargs()` centraliza la construcción de kwargs para `complete()` y `stream()`, evitando duplicación del manejo de `system` y `json_mode`.
- `OllamaLLMAdapter._chat_payload()` inserta el `system` como primer mensaje con rol `system` (formato messages de Ollama).

---

### 3.1 Arranque del Proyecto — Estructura Hexagonal Completa (Backend + Frontend)

**Fecha**: 2026-04-28  
**Modelo**: claude-sonnet-4-6  
**Resultado**: Estructura completa de carpetas y ficheros stub del proyecto siguiendo arquitectura hexagonal: dominio, puertos, adaptadores, casos de uso, API FastAPI, frontend React/TypeScript y tests espejo.  
**Ficheros generados/afectados**:
- `backend/src/domain/entities/` — Task, Project, Sprint, Estimation, Report, KnowledgeChunk
- `backend/src/domain/ports/` — 10 puertos abstractos (LLMPort, EmbeddingPort, VectorStorePort, TaskRepositoryPort, ProjectRepositoryPort, SprintRepositoryPort, JiraPort, ConfluencePort, GitHubPort, DocumentGeneratorPort)
- `backend/src/domain/services/` — EstimationService, PlanningService, RAGService
- `backend/src/application/use_cases/` — 9 use cases stub
- `backend/src/application/commands/` — 4 commands/DTOs
- `backend/src/adapters/primary/api/` — 8 FastAPI routers
- `backend/src/adapters/primary/websocket/` — chat WebSocket handler
- `backend/src/adapters/secondary/` — LLM (Claude, Ollama, Groq, Gemini), Embedding, ChromaDB, PostgreSQL, Jira, Confluence, GitHub
- `backend/src/infrastructure/` — LLMRouter, TaskClassifier, RAG pipeline, Settings, Container, main.py
- `backend/pyproject.toml` + `backend/alembic/` + `backend/tests/`
- `frontend/src/` — tipos, servicios, hooks, componentes, páginas
- `frontend/` — vite.config.ts, tsconfig.json, package.json, manifest.json PWA
- `CHANGELOG.md` — creado

**Prompt**:

```
Lee CLAUDE.md, docs/ARCHITECTURE.md, docs/ADR-001-stack.md y docs/FUNCTIONAL_SPEC.md antes de empezar. Vamos a arrancar el desarrollo del PM Copilot siguiendo la arquitectura hexagonal definida. El primer paso es crear la estructura completa de carpetas y ficheros stub del proyecto, tanto para el backend (Python/FastAPI) como para el frontend (React/TypeScript). No implementes lógica todavía, solo la estructura con stubs documentados que reflejen la arquitectura hexagonal: dominio, puertos, adaptadores, casos de uso y API. Incluye también la estructura de tests espejando el backend. Cuando termines activa el skill docs-updater para actualizar CLAUDE.md si es necesario. Activa también el skill prompt-librarian para registrar este prompt en docs/PROMPTS.md con el contexto "Prompt de arranque del desarrollo — creación de estructura del proyecto" y publícalo en Confluence usando scripts/publish_prompts.py.
```

**Notas**:
- Prompt de arranque de desarrollo. Funcionó en una sola pasada generando ~60 ficheros.
- El modelo leyó los 4 documentos de referencia antes de generar código, produciendo output coherente con la arquitectura definida.
- Los stubs Python usan `raise NotImplementedError` con `# TODO:` detallando qué implementar — facilita que la IA retome el trabajo en sesiones futuras.
- Los stubs TypeScript usan `throw new Error("Not implemented")` con el mismo patrón.
- La dependencia `LLMRouter → tenacity` está reflejada en los stubs con decoradores `@retry` importados, lista para implementar.
- Reutilizable en: cualquier proyecto nuevo con arquitectura hexagonal — cambiar entidades de dominio y puertos según el dominio de negocio.
- Variación sugerida: añadir `docker-compose.yml` y `.env.example` al mismo prompt.
- No usar cuando: el proyecto ya tiene código existente que podría sobrescribirse.

### 3.2 Infraestructura Local — Docker Compose, DDL y Makefile

**Fecha**: 2026-04-28  
**Modelo**: claude-sonnet-4-6  
**Resultado**: Entorno de desarrollo local completo: docker-compose.yml (PostgreSQL 16 + ChromaDB + pgAdmin), DDL con 7 tablas y 26 índices, Makefile con comandos operacionales, .env.example completo.  
**Ficheros generados/afectados**:
- `docker-compose.yml` — PostgreSQL 16-alpine, ChromaDB latest, pgAdmin (profile tools), red pmcopilot-net
- `scripts/db_init.sql` — 7 tablas, 26 índices, trigger set_updated_at
- `Makefile` — targets up/down/db-init/logs/db-shell/tools-up/db-reset/ps/help
- `.env.example` — variables PostgreSQL, ChromaDB, pgAdmin, LLM_MODE, SECRET_KEY
- `.env` — variables POSTGRES_* y CHROMADB_* añadidas al fichero existente

**Prompt**:

```
Crea docker-compose.yml en la raíz del proyecto con:

- PostgreSQL 16:
  - Variables desde .env (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT)
  - Healthcheck con pg_isready
  - Volumen persistente postgres_data
  - Puerto mapeado al host

- ChromaDB latest:
  - Puerto 8001
  - Volumen persistente chroma_data
  - Variable ANONYMIZED_TELEMETRY=false

- pgAdmin (profile "tools", opcional):
  - Puerto 5050
  - Variables PGADMIN_EMAIL, PGADMIN_PASSWORD desde .env

- Red interna "pmcopilot-net" para todos los servicios

Crea scripts/db_init.sql con DDL completo para:
  - tasks (id, title, description, status, priority, estimation_points, 
    project_id, sprint_id, created_at, updated_at)
  - projects (id, name, description, jira_key, created_at, updated_at)
  - sprints (id, name, project_id, start_date, end_date, status, created_at)
  - estimations (id, task_id, points, reasoning, confidence, model_used, created_at)
  - knowledge_chunks (id, content, embedding_id, source, metadata jsonb, created_at)

Todas las tablas con UUID como PK, índices en foreign keys y campos de búsqueda frecuente.

Actualiza .env.example con todas las variables nuevas.

Añade al Makefile:
  - make up      → docker-compose up -d
  - make down    → docker-compose down
  - make db-init → ejecuta db_init.sql contra PostgreSQL
  - make logs    → docker-compose logs -f
```

**Notas**:
- El truco clave del `db-init`: `docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER"'  < archivo.sql` — ejecuta psql dentro del contenedor usando sus variables de entorno nativas, y recibe el SQL del host por stdin.
- El Makefile usa `-include .env` + `export` para inyectar variables en targets que necesiten acceder al host (ej. `db-shell`), pero para `db-init` el contenedor ya tiene las variables de entorno propias.
- El `POSTGRES_PORT` faltaba en el `.env` existente y causó que el contenedor arrancara con credenciales vacías; se detectó en la primera ejecución y se corrigió añadiéndolo al `.env`.
- El índice único parcial `WHERE status = 'active'` en sprints elimina lógica de validación en capa de aplicación.
- Reutilizable en: cualquier proyecto FastAPI + PostgreSQL + ChromaDB. Cambiar nombres de tablas y columnas según el dominio.
- Variación sugerida: añadir un `docker-compose.override.yml` para producción (Railway) vs desarrollo local.
- No usar cuando: el entorno usa Podman (hay incompatibilidades en el formato de healthcheck).

---

### 3.3 EstimationService + EstimateTaskUseCase + endpoint REST (PMCP-11)

**Fecha**: 2026-04-30  
**Modelo**: claude-sonnet-4-6  
**Resultado**: Caso de uso vertical completo de estimación: `EstimationService` con Fibonacci + RAG, `EstimateTaskUseCase`, `POST /api/v1/estimate` y `POST /api/v1/estimate/breakdown`. 12 tests unitarios. Suite: 30 passed.  
**Ficheros generados/afectados**:
- `backend/src/domain/services/estimation_service.py`
- `backend/src/domain/entities/estimation.py` (`is_high_confidence()`)
- `backend/src/application/use_cases/estimate_task_use_case.py`
- `backend/src/adapters/primary/api/estimate_router.py`
- `backend/src/infrastructure/container.py` (propiedad `estimate_task_use_case`)
- `backend/tests/unit/domain/services/test_estimation_service.py`
- `backend/tests/unit/application/use_cases/test_estimate_task_use_case.py`

**Prompt**:

```
Implementa la épica PMCP-11 (primer caso de uso vertical: EstimateTask).

PMCP-12 — EstimationService en backend/src/domain/services/estimation_service.py:
- estimate(task, similar_chunks) -> Estimation: construye prompt con escala Fibonacci
  (1,2,3,5,8,13,21), incluye chunks similares como contexto, llama al LLM con
  json_mode=True y task_type=REASONING. Parsea JSON: points, confidence, breakdown,
  rationale. Snappea points al Fibonacci más cercano con min(FIBONACCI, key=lambda x: abs(x-p)).
  Clamp confidence en [0,1].
- breakdown_epic(epic_task) -> list[Task]: descompone épica en ≤15 stories usando
  task_type=GENERATION_LONG. Parsea lista JSON de títulos/descripciones.
- Estimation.is_high_confidence(): retorna True si confidence >= 0.7

PMCP-13 — EstimateTaskUseCase en backend/src/application/use_cases/estimate_task_use_case.py:
- execute(command: EstimateTaskCommand) -> EstimateTaskResult
- Flujo: embed(title+description) → vector_store.search(collection="tasks", top_k=5,
  filter=project_id) → Task transiente → EstimationService.estimate()
- Task es transiente (no persiste hasta PMCP-27)

PMCP-14 — Endpoints en backend/src/adapters/primary/api/estimate_router.py:
- POST /api/v1/estimate: recibe {project_id, title, description}, retorna estimación
- POST /api/v1/estimate/breakdown: recibe {project_id, title, description}, retorna lista
- DI via Depends() desde container. 422 si LLM devuelve JSON inválido (ValueError)

PMCP-15 — Tests unitarios (sin llamadas reales):
- 9 tests para EstimationService: Fibonacci snap, JSON inválido, confidence clamp,
  similar_chunks en prompt, max 15 stories, tipos de output
- 3 tests para EstimateTaskUseCase: embed llamado con title+description, search con project_id,
  resultado contiene task_id y estimation válida
```

**Notas**:
- `min(FIBONACCI_POINTS, key=lambda x: abs(x - points))` es la forma idiomática de snap-to-nearest; maneja cualquier valor devuelto por el LLM incluyendo 0 o negativos.
- El prompt de sistema de EstimationService incluye los `similar_chunks` formateados como `[source] content[:300]` — truncar a 300 caracteres evita exceder el contexto del LLM en proyectos con chunks grandes.
- Si el LLM devuelve JSON inválido, `estimate()` lanza `ValueError` que el router convierte en 422. El criterio de aceptación está en `DEFINITION_OF_DONE.md`.
- `breakdown_epic()` usa `GENERATION_LONG` en lugar de `REASONING` porque genera texto extenso (lista de historias), no un razonamiento compacto.
- Reutilizable en: cualquier caso de uso que necesite output JSON estructurado del LLM — el patrón `json_mode=True` + `try/except json.JSONDecodeError` + fallback 422 es replicable.
- No usar cuando: la estimación necesita consenso de equipo o historial de velocidad real — el LLM solo tiene acceso a los chunks indexados.

---

### 3.4 Chat API REST + WebSocket streaming con RAG (PMCP-16/17/18)

**Fecha**: 2026-05-01  
**Modelo**: claude-sonnet-4-6  
**Resultado**: `QueryProjectStatusUseCase` funcional, store en memoria para sesiones/mensajes, WebSocket handler con RAG + streaming de tokens. 10 tests unitarios. Suite: 40 passed.  
**Ficheros generados/afectados**:
- `backend/src/domain/entities/project.py` (`Sprint.is_active()`, `Project.active_sprint()`)
- `backend/src/application/use_cases/query_project_status_use_case.py`
- `backend/src/adapters/primary/api/chat_router.py`
- `backend/src/adapters/primary/websocket/chat_ws_handler.py`
- `backend/tests/unit/application/use_cases/test_query_project_status_use_case.py`

**Prompt**:

```
Implementa la épica PMCP-16 (Chat con streaming).

PMCP-17 — QueryProjectStatusUseCase:
- execute(project_id) -> ProjectStatusResult
- completed_points: suma de estimated_points de tareas con status=DONE
- remaining_points: suma del resto
- blocked_task_count: tareas con status=IN_REVIEW y priority IN {HIGH, CRITICAL}
- days_remaining: (sprint.end_date - now).days, nunca negativo, None si no hay sprint activo
- Sprint.is_active(): status == SprintStatus.ACTIVE
- Project.active_sprint(sprints): next((s for s in sprints if s.is_active()), None)
- 10 tests unitarios en 3 clases: TestPointsAggregation, TestBlockedTaskCount, TestActiveSprint

PMCP-18 — Chat API REST + WebSocket streaming:
- chat_router.py: store en memoria _sessions/_messages (placeholder hasta PMCP-27)
  POST /api/v1/chat/sessions, POST /sessions/{id}/messages → {message_id, stream_url},
  GET /sessions/{id}/messages. Helpers: get_pending_message(), save_assistant_response()
- chat_ws_handler.py: WebSocket en /api/v1/chat/stream/{message_id}
  1. get_pending_message(message_id) → error+close si no existe
  2. embed(content) → vector_store.search(collection="tasks", top_k=3, filter=project_id)
     — wrap en try/except para que el chat funcione aunque el vector store esté vacío
  3. Construir prompt: "Project context:\n{context}\n\nUser: {content}"
  4. LLMRequest(task_type=SIMPLE_QA, max_tokens=1024, temperature=0.5)
  5. async for token in llm_router.stream(): send_json({"type":"token","content":token})
  6. save_assistant_response(); send_json({"type":"done","sources":[...]})
```

**Notas**:
- El store en memoria (`_sessions`, `_messages` como dicts a nivel módulo) es un placeholder consciente, no una decisión de diseño. El comentario `# In-memory store — replaced by PostgreSQL adapter in PMCP-27` lo deja claro en el código.
- La RAG retrieval está en un `try/except Exception` separado: si ChromaDB no está disponible o la colección está vacía, el chat sigue funcionando sin contexto. Los errores se logean como `WARNING`, no `ERROR`.
- `save_assistant_response()` crea un mensaje nuevo con `role="assistant"` en lugar de mutar el mensaje de usuario — mantiene consistencia con el modelo de datos de chat_sessions.
- El `system` prompt fijo (`_SYSTEM_PROMPT`) define el rol del asistente; el contexto RAG va en el `prompt` del usuario, no en el system. Esto mantiene separación entre instrucciones del sistema y contexto dinámico.
- Reutilizable en: cualquier handler WebSocket de streaming — el patrón `accept → validate → build_context → stream_tokens → send_done` es el esqueleto estándar.
- No usar cuando: el proyecto requiere persistencia de sesiones entre reinicios — este store se pierde en cada restart.

---

### 3.5 OllamaEmbeddingAdapter + ChromaDBAdapter (PMCP-22/23)

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: Dos adaptadores secundarios implementados sobre stubs — `OllamaEmbeddingAdapter` con httpx puro y `ChromaDBAdapter` con AsyncHttpClient lazy. Circuit breakers con tenacity en ambos.
**Ficheros generados/afectados**:
- `backend/src/adapters/secondary/embedding/ollama_embedding_adapter.py`
- `backend/src/adapters/secondary/vector_store/chromadb_adapter.py`

**Prompt**:

```
Implementa PMCP-22 y PMCP-23 de la épica RAG.

PMCP-22 — OllamaEmbeddingAdapter en backend/src/adapters/secondary/embedding/ollama_embedding_adapter.py:
- Implementa EmbeddingPort
- embed(text) -> list[float]: POST httpx a {base_url}/api/embeddings con
  {"model": "nomic-embed-text", "prompt": text}. Valida que len(result) == 768.
  Si la dimensión es incorrecta lanza ValueError.
- embed_batch(texts) -> list[list[float]]: asyncio.gather paralelo sobre embed()
- dimension property: retorna 768
- Circuit breaker: @retry tenacity sobre embed(), 3 intentos, backoff exponencial,
  retry solo en ConnectError/TimeoutException/RemoteProtocolError

PMCP-23 — ChromaDBAdapter en backend/src/adapters/secondary/vector_store/chromadb_adapter.py:
- Implementa VectorStorePort
- _get_client(): lazy init, await chromadb.AsyncHttpClient(host, port)
  (AsyncHttpClient es una corutina en chromadb >= 0.5, necesita await)
- upsert(id, embedding, content, metadata, collection): get_or_create_collection + col.upsert
- search(query_embedding, collection, top_k, filter): get_collection (retorna [] si no existe),
  col.query con include=["documents", "metadatas", "distances"],
  score = round(1.0 - distances[i], 4)
- delete(id, collection): silencioso si no existe
- collection_exists(collection): bool
- Circuit breaker: @retry tenacity en upsert y search, 3 intentos, backoff exponencial
```

**Notas**:
- `await chromadb.AsyncHttpClient(host, port)` — `AsyncHttpClient` en chromadb ≥0.5 es una corutina, no un constructor. Olvidar el `await` da `AttributeError` en la primera llamada.
- `score = 1 - distance` convierte la distancia coseno de ChromaDB (0=idéntico) en similitud (1=idéntico).
- El `try/except` en `search()` cuando la colección no existe evita que el chat falle en proyectos recién creados sin chunks indexados.
- Los tipos retryables de httpx son `ConnectError`, `TimeoutException`, `RemoteProtocolError` — no incluir `HTTPStatusError` (un 4xx no se recupera reintentando).
- Reutilizable en: cualquier adaptador de embedding local — cambiar el modelo y la dimensión esperada.

---

### 3.6 RAGService + DocumentChunker + IndexDocumentsUseCase + QueryKnowledgeUseCase (PMCP-24/25)

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: Pipeline RAG completo: `DocumentChunker` en capa de dominio, `RAGService`, `IndexDocumentsUseCase` con `BackgroundTasks`, `QueryKnowledgeUseCase` con fallback, y router `/knowledge`.
**Ficheros generados/afectados**:
- `backend/src/domain/services/chunker.py` (movido desde infrastructure — fix hexagonal)
- `backend/src/infrastructure/rag/chunker.py` (re-export)
- `backend/src/domain/services/rag_service.py`
- `backend/src/application/use_cases/index_documents_use_case.py`
- `backend/src/application/use_cases/query_knowledge_use_case.py`
- `backend/src/adapters/primary/api/knowledge_router.py`
- `backend/src/infrastructure/container.py`

**Prompt**:

```
Implementa la épica PMCP-21 (RAG y base de conocimiento).

DocumentChunker en backend/src/domain/services/chunker.py (NO en infrastructure — hexagonal):
- CHUNK_SIZE=512 palabras, CHUNK_OVERLAP=50 palabras
- chunk_markdown(content, source, doc_id, project_id, url, last_updated):
  split por headings ## / ###, secciones grandes re-split con _split_with_overlap;
  fallback a chunk_plain_text si no hay headings
- chunk_plain_text(content, source, doc_id, project_id, url, last_updated):
  split fijo con overlap; retorna [] si content vacío
- _make_chunk(): crea KnowledgeChunk con uuid4, project_id, source, section, url

RAGService en backend/src/domain/services/rag_service.py:
- KNOWLEDGE_COLLECTION = "knowledge"
- index_chunk(chunk): embed(content) → vector_store.upsert(metadata con project_id, source)
  Almacena embedding en chunk.embedding
- index_chunks(chunks): asyncio.gather sobre index_chunk()
- search(query, project_id, top_k=5): embed(query) → vector_store.search(filter={"project_id":...})

PMCP-24 — IndexDocumentsUseCase:
- Constructor: rag_service, confluence_port, jira_port, github_port, chunker (inyectado)
- execute(command: IndexDocumentsCommand) -> IndexDocumentsResult
- Por cada source: _fetch_and_chunk() → index_chunks(); error en source → failed++
- _index_confluence: list_pages(space_key) → por página get_page_content → chunk_plain_text
- _index_jira: list_issues(project_key) → "{summary}\n\n{description}" → chunk_plain_text
- _index_github: get_file_content para README.md, docs/ARCHITECTURE.md, docs/PRD.md → chunk_markdown
- FastAPI: POST /api/v1/knowledge/index retorna 202 con BackgroundTasks

PMCP-25 — QueryKnowledgeUseCase:
- execute(cmd: KnowledgeQueryCommand) -> KnowledgeQueryResult
- rag_service.search(query, project_id, top_k) → si [] retornar fallback "No se encontró..."
- Construir prompt: "Context:\n{chunks}\n\nQuestion: {query}"
- LLMRequest(task_type=SIMPLE_QA), NO llamar al LLM si no hay resultados
- Retornar KnowledgeQueryResult(answer, sources=search_results)
```

**Notas**:
- `DocumentChunker` solo depende de `domain.entities.knowledge` — no tiene dependencias de infraestructura. Por eso vive en `domain/services/`, no en `infrastructure/`. Colocarlo en infrastructure sería una violación hexagonal: `application/` no puede importar de `infrastructure/`.
- `asyncio.gather` en `index_chunks()` paraleliza los embeddings — con 100 chunks, el tiempo es O(1 embedding) en lugar de O(100).
- El `chunker` se inyecta en el constructor de `IndexDocumentsUseCase` (no se instancia internamente) para hacer el use case testeable sin imports de infraestructura.
- Reutilizable en: cualquier pipeline RAG — el patrón chunk → embed → upsert es estándar, solo cambiar las fuentes en `_fetch_and_chunk`.
- No usar cuando: el volumen de documentos es >10k páginas — evaluar procesamiento en batch con rate limiting por fuente.

---

### 3.7 Épica de Persistencia PostgreSQL — ORM, Alembic y Adapters (PMCP-27/28/29/30)

**Fecha**: 2026-05-04
**Modelo**: claude-sonnet-4-6
**Resultado**: Épica completa de persistencia implementada: modelos ORM SQLAlchemy 2.0, tres adapters (Task, Project, Sprint), migración Alembic async, Container actualizado, 18 tests de integración contra PostgreSQL real. Suite: 137 passed.
**Ficheros generados/afectados**:
- `backend/src/domain/exceptions.py` (nuevo — `DomainError`)
- `backend/src/adapters/secondary/persistence/models.py` (nuevo — `ProjectORM`, `SprintORM`, `TaskORM`)
- `backend/src/adapters/secondary/persistence/postgresql_task_adapter.py` (implementado)
- `backend/src/adapters/secondary/persistence/postgresql_project_adapter.py` (implementado)
- `backend/src/infrastructure/container.py` (propiedades `db_session_factory`, `task_repo`, `project_repo`, `sprint_repo`)
- `backend/src/infrastructure/config/settings.py` (env_file múltiple)
- `backend/alembic.ini` (nuevo)
- `backend/alembic/env.py` (actualizado con Base.metadata y settings)
- `backend/alembic/versions/001_initial_schema.py` (nuevo)
- `Makefile` (targets `migrate`, `migrate-down`)

**Prompt**:

```
Proseguimos con la épica de persistencia (PMCP-27).

Contexto previo: el proyecto tiene arquitectura hexagonal con PostgreSQL + ChromaDB.
Los puertos TaskRepositoryPort, ProjectRepositoryPort, SprintRepositoryPort están definidos
en domain/ports/. Los stubs de adaptadores existen en adapters/secondary/persistence/
con NotImplementedError. El schema de BD está en scripts/db_init.sql (7 tablas, 26 índices).

Implementa PMCP-28, 29, 30 y 31 en orden de dependencias:

PMCP-28 — PostgreSQLTaskAdapter:
- ORM models en models.py: Base (DeclarativeBase), ProjectORM, SprintORM, TaskORM
  con SQLAlchemy 2.0 Mapped/mapped_column. tags: ARRAY(Text). Enums como String (VARCHAR).
- Constructor: session_factory: async_sessionmaker[AsyncSession]
- Métodos: get_by_id (session.get), list_by_project (select con filtros opcionales),
  save (merge + flush = upsert), delete (get + delete si existe),
  list_pending_jira_sync (WHERE jira_sync_status='pending')
- Conversiones _to_orm() y _to_entity() completas

PMCP-29 — PostgreSQLProjectAdapter + PostgreSQLSprintAdapter:
- PostgreSQLProjectAdapter: get_by_id, list_all (ORDER BY created_at DESC), save, delete
- PostgreSQLSprintAdapter: get_by_id, get_active (WHERE status='active'), list_by_project, save
- save() de SprintAdapter captura sqlalchemy.exc.IntegrityError y relanza como DomainError
  (violación del índice único parcial uq_sprints_one_active_per_project)
- DomainError en domain/exceptions.py (clase base de excepciones de negocio)

PMCP-30 — Alembic:
- alembic.ini en backend/ con prepend_sys_path = .
- env.py importa Base desde models, settings.database_url como URL
- settings.py: env_file=[".env", "../.env"] para funcionar desde backend/ y desde raíz
- Migración 001_initial_schema.py: un op.execute() por sentencia DDL (asyncpg no soporta
  multi-statement en una sola llamada). Usar IF NOT EXISTS para idempotencia.
- make migrate / make migrate-down en Makefile

PMCP-31 — Tests de integración:
- tests/integration/conftest.py: fixture session_factory (scope=function, fresh engine por test),
  fixture clean_db autouse (TRUNCATE projects CASCADE antes de cada test),
  fixture saved_project
- test_postgresql_task_adapter.py: 7 tests (save+retrieve con tags ARRAY, list con filtro,
  pending sync, delete, upsert, noop delete)
- test_postgresql_project_adapter.py: 11 tests (project CRUD + cascade, sprint get_active,
  segundo sprint activo → DomainError, list_by_project)
```

**Notas**:
- asyncpg no soporta múltiples comandos en una sola `execute()` call — `cannot insert multiple commands into a prepared statement`. Cada sentencia DDL en la migración debe ser un `op.execute()` separado.
- `session.merge()` en SQLAlchemy 2.0 async es awaitable: `await session.merge(orm)`. Hace INSERT si la PK no existe, UPDATE si existe — implementación correcta de upsert sin ON CONFLICT.
- `async_sessionmaker` con `expire_on_commit=False` evita `MissingGreenlet` en tests cuando se accede a atributos del objeto después de `commit()`.
- Para tests de integración async con pytest-asyncio: usar `scope="function"` para el engine (no "session") — los engines compartidos entre tests con diferentes event loops causan "cannot perform operation: another operation is in progress".
- `settings.py` con `env_file=[".env", "../.env"]` es el patrón para proyectos donde Alembic se ejecuta desde `backend/` pero el `.env` está en la raíz del proyecto.
- Reutilizable en: cualquier proyecto FastAPI + SQLAlchemy 2.0 con async — los patrones de models.py, session_factory en Container, y conftest.py de integración son directamente aplicables.
- Variación sugerida para proyectos con muchos adaptadores: crear una clase base `BaseSQLAdapter` con `_session_factory` y los helpers `_to_orm`/`_to_entity` como métodos abstractos.
- No usar cuando: el volumen de escrituras requiere bulk inserts — `merge()` hace SELECT + INSERT/UPDATE por fila, no es eficiente para operaciones masivas.

---

## 4. Prompts de Desarrollo Frontend

### 4.1 useCopilotChat hook + componentes Chat (PMCP-19/20)

**Fecha**: 2026-05-01  
**Modelo**: claude-sonnet-4-6  
**Resultado**: Hook `useCopilotChat` con gestión optimista de mensajes + WebSocket, y componentes `ChatInput`, `MessageBubble`, `ChatWindow`, `ChatPage` completamente funcionales.  
**Ficheros generados/afectados**:
- `frontend/src/services/chatService.ts`
- `frontend/src/hooks/useCopilotChat.ts`
- `frontend/src/hooks/useProjectContext.ts` (stub sin throws)
- `frontend/src/components/chat/ChatInput.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/ChatWindow.tsx`
- `frontend/src/components/ui/LoadingSpinner.tsx`
- `frontend/src/pages/ChatPage.tsx`

**Prompt**:

```
Implementa PMCP-19 y PMCP-20 (frontend del chat con streaming).

PMCP-19 — chatService.ts + useCopilotChat hook:
chatService:
- API_BASE desde import.meta.env.VITE_API_URL ?? "http://localhost:8080"
- WS_BASE = API_BASE.replace(/^http/, "ws")
- createSession(projectId), listSessions(), sendMessage(sessionId, content),
  getMessages(sessionId) — todos via fetch con error si !res.ok
- streamResponse(messageId, onToken, onDone, onError): abre WebSocket,
  parsea JSON de cada evento, despacha a callbacks

useCopilotChat():
- Estado: messages[], session, isStreaming, sources[]
- startSession(projectId): POST → setSession, clearMessages
- sendMessage(content):
  1. Añadir mensaje user al estado inmediatamente (optimista)
  2. Añadir placeholder assistant con content=""
  3. POST sendMessage → obtener message_id
  4. Abrir WebSocket via chatService.streamResponse()
  5. onToken: actualizar content del placeholder acumulando tokens
  6. onDone: setSources, setIsStreaming(false), ws.close()
  7. onError: content="Error: {detail}", setIsStreaming(false)
- clearMessages(): reset messages y sources

PMCP-20 — Componentes React (inline styles, sin CSS framework):
- LoadingSpinner({size, label}): div circular con animation CSS "@keyframes pmcp-spin"
- MessageBubble({message}): burbuja con justify flex-end para user, flex-start para assistant;
  cursor parpadeante (▋) cuando content está vacío (streaming en progreso)
- ChatInput({onSend, disabled}): textarea auto-resize via scrollHeight, Enter envía,
  Shift+Enter nueva línea, botón Send deshabilitado si disabled o content vacío
- ChatWindow({messages, isStreaming, onSend}): lista de MessageBubble + auto-scroll
  via useRef+scrollIntoView, LoadingSpinner cuando isStreaming, ChatInput al fondo
- ChatPage: si !session → pantalla con input de Project ID UUID + botón Start Chat;
  si session → header azul + ChatWindow a pantalla completa
```

**Notas**:
- El patrón de mensajes optimistas (añadir user + placeholder assistant antes de la llamada HTTP) evita el salto visual que ocurriría esperando el primer token.
- `useRef` para el WebSocket (`wsRef`) en lugar de estado — los WebSockets son recursos externos, no parte del estado de render. Cerrar el WS anterior antes de abrir uno nuevo evita leaks si el usuario envía mensajes rápido.
- Sin dependencia de librería de Markdown para el MVP — `white-space: pre-wrap` renderiza saltos de línea del LLM correctamente. Añadir `react-markdown` cuando el formato de respuestas lo justifique.
- `useProjectContext` se implementó como stub sin throws (retorna estado vacío) en lugar de conectar al backend — desbloquea ChatPage sin necesitar PMCP-27 (persistencia).
- `VITE_API_URL` en `.env` del frontend apunta a `http://localhost:8080`; en producción (Vercel) se configura como variable de entorno apuntando al backend en Railway.
- Reutilizable en: cualquier interfaz de chat con streaming WebSocket — el hook es independiente del dominio, solo necesita adaptar `chatService`.
- No usar cuando: la interfaz necesita historial persistente entre sesiones — el hook almacena mensajes solo en memoria React.

---

## 5. Prompts de Testing

### 5.1 Tests unitarios del LLMRouter con AsyncMock y cobertura ≥90%

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: 14 tests en `tests/unit/infrastructure/test_llm_router.py`, 98% cobertura de `llm_router.py`, sin llamadas reales a APIs. Cubre LOCAL/HYBRID mode, fallback entre proveedores, streaming con fallo y recuperación, health check.
**Ficheros generados/afectados**: `backend/tests/unit/infrastructure/test_llm_router.py`

**Prompt**:

```
Implementa tests en backend/tests/unit/infrastructure/test_llm_router.py usando AsyncMock
para todos los puertos LLM. Tests requeridos:

- test_local_mode_uses_ollama_only: verifica que en LOCAL solo se llama ollama.complete
- test_fallback_to_ollama_when_claude_fails: claude lanza Exception, ollama retorna respuesta válida
- test_reasoning_uses_claude_first_when_available: HYBRID+REASONING → claude primero
- test_classification_uses_groq_first: HYBRID+CLASSIFICATION → groq primero
- test_all_providers_fail_raises: todos fallan → RuntimeError
- tests de streaming: stream() yields tokens, fallback cuando primer provider falla, raise cuando todos fallan
- tests de health_check: True si al menos uno OK, False si todos fallan

Restricciones:
- Solo AsyncMock, sin llamadas reales a APIs ni red
- pytest-asyncio en modo AUTO (asyncio_mode = "auto" en pyproject.toml)
- Cobertura de llm_router.py ≥ 90%
- LLMRouter debe instanciarse con retry_attempts=1 en tests para evitar backoff de tenacity
```

**Notas**:
- La primera iteración alcanzó 81% de cobertura porque `stream()` no estaba cubierto. Se añadió la clase `TestStreaming` con 3 tests para llegar a 98%.
- Los generators async para mocking de `stream()` requieren definir funciones `async def` que hagan `yield`, no `AsyncMock` directamente — `AsyncMock` no soporta `async for` sobre su return value por defecto.
- `retry_attempts=1` en el constructor del `LLMRouter` es el patrón para desactivar los sleeps de tenacity en tests sin mockear el módulo entero.

---

### 5.2 Tests unitarios QueryProjectStatusUseCase — 3 clases, 10 tests (PMCP-17)

**Fecha**: 2026-05-01  
**Modelo**: claude-sonnet-4-6  
**Resultado**: `test_query_project_status_use_case.py` con 10 tests en 3 clases. Cubre agregación de puntos, tareas bloqueadas y gestión del sprint activo incluyendo fechas naive/aware y resultado nunca negativo.  
**Ficheros generados/afectados**: `backend/tests/unit/application/use_cases/test_query_project_status_use_case.py`

**Prompt**:

```
Escribe tests unitarios para QueryProjectStatusUseCase en
tests/unit/application/use_cases/test_query_project_status_use_case.py.

Helpers locales (no fixtures globales):
- make_task(project_id, status, priority, points) -> Task con campo jira_sync_status
- make_sprint(project_id, status, name, end_date) -> Sprint
- make_use_case(tasks, sprint) -> QueryProjectStatusUseCase con repos como AsyncMock

Clases de test:
1. TestPointsAggregation:
   - test_completed_and_remaining_points: 2 DONE (8p) + 2 no-DONE (10p) → totales correctos
   - test_none_points_treated_as_zero: estimated_points=None → 0
   - test_empty_project_returns_zeros: sin tareas → 0,0,0

2. TestBlockedTaskCount:
   - test_in_review_high_priority_counts_as_blocked: IN_REVIEW+HIGH y IN_REVIEW+CRITICAL
     cuentan; IN_REVIEW+MEDIUM y IN_PROGRESS+HIGH no cuentan
   - test_no_blocked_tasks: DONE+CRITICAL y IN_REVIEW+LOW → blocked=0

3. TestActiveSprint:
   - test_active_sprint_name_returned
   - test_no_active_sprint_returns_none: days_remaining=None, active_sprint_name=None
   - test_days_remaining_computed_correctly: end_date = now+5.5d → days_remaining=5
     (usar +12h buffer para evitar que timedelta.days truncue a 4)
   - test_days_remaining_never_negative: end_date en el pasado → days_remaining=0
   - test_naive_end_date_handled: datetime sin tzinfo se normaliza a UTC
```

**Notas**:
- `timedelta.days` trunca hacia abajo (floor), no redondea — `now + timedelta(days=5)` da 4 si hay microsegundos de diferencia entre la construcción del end_date y la ejecución del use case. Solución: añadir buffer de `timedelta(hours=12)` al end_date en el test.
- Los helpers locales (`make_task`, `make_sprint`, `make_use_case`) son preferibles a fixtures en conftest para tests de use cases: hacen el test autocontenido y evitan dependencias ocultas con el scope de fixtures globales.
- `AsyncMock(spec=TaskRepositoryPort)` + `return_value` directamente — no necesita configuración adicional porque el use case solo llama `list_by_project` y `get_active`.
- Reutilizable en: cualquier use case que agregue datos de repositorios — el patrón `make_X` + `make_use_case` + clase de test por aspecto funciona en todos los contextos similares.

---

### 5.3 Tests RAG — RAGService, DocumentChunker, OllamaEmbeddingAdapter, IndexDocumentsUseCase, QueryKnowledgeUseCase (PMCP-21)

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: 5 ficheros de test, 37 tests nuevos, cobertura de todos los módulos de la épica RAG. Suite total: 78 passed, 3 skipped.
**Ficheros generados/afectados**:
- `backend/tests/unit/domain/services/test_rag_service.py`
- `backend/tests/unit/infrastructure/test_document_chunker.py`
- `backend/tests/unit/application/use_cases/test_query_knowledge_use_case.py`
- `backend/tests/unit/adapters/secondary/test_ollama_embedding_adapter.py`
- `backend/tests/unit/application/use_cases/test_index_documents_use_case.py`

**Prompt**:

```
Escribe tests unitarios para todos los módulos de la épica PMCP-21 (RAG).

test_rag_service.py:
- TestIndexChunk: embeds y upserts, embedding almacenado en chunk, metadata con project_id y source
- TestIndexChunks: todos los chunks indexados (assert await_count == N)
- TestSearch: embed query → vector_store.search con filter, retorna resultados, vacío si no hay

test_document_chunker.py:
- TestChunkMarkdown: split en headings, heading en section, fallback sin headings,
  sección grande re-split, project_id correcto, url propagada
- TestChunkPlainText: chunk único corto, múltiples chunks largo, overlap verificado
  (últimas CHUNK_OVERLAP palabras del chunk 1 == primeras del chunk 2), vacío retorna [],
  section=None

test_query_knowledge_use_case.py:
- retorna answer con sources, fallback "No se encontró" cuando no hay resultados,
  LLM NO llamado cuando no hay resultados,
  contexto incluido en el prompt (verificar call_args),
  search llamado con project_id y top_k

test_ollama_embedding_adapter.py:
- embedding correcto en éxito, POST al endpoint correcto con model y prompt,
  ValueError con dimensión incorrecta, trailing slash stripped,
  embed_batch retorna todos, batch vacío retorna []

test_index_documents_use_case.py:
- Confluence: indexa páginas, skip sin space_key, skip con port=None,
  error en get_page_content salta esa página pero continúa
- Jira: indexa issues, skip sin project_key
- GitHub: indexa ficheros, fichero faltante silencioso
- Múltiples fuentes: procesa todas, error en index_chunks incrementa failed_count
```

**Notas**:
- `patch("httpx.AsyncClient")` con `__aenter__`/`__aexit__` AsyncMock es el patrón para mockear context managers async de httpx. Alternativa: usar `respx` si hay muchas llamadas.
- Para verificar el overlap entre chunks: `chunks[0].content.split()[-CHUNK_OVERLAP:] == chunks[1].content.split()[:CHUNK_OVERLAP]`.
- `MagicMock(spec=DocumentChunker)` para el chunker en tests de `IndexDocumentsUseCase` — retorna listas configurables sin ejecutar el chunking real.
- El patrón `make_use_case()` que retorna tupla `(uc, rag, confluence, jira, github)` permite aserciones precisas sobre qué puerto fue llamado y con qué argumentos.
- Los errores por página (Confluence) y por fichero (GitHub) se loguean como WARNING y se continúa — los tests verifican que el source sigue siendo procesado si al menos un documento tuvo éxito.

---

### 5.4 Code review cross-épicas — tests de entidades, LLM adapters y task classifier

**Fecha**: 2026-05-01
**Modelo**: claude-sonnet-4-6
**Resultado**: 41 tests nuevos cubriendo módulos no testeados de PMCP-1, PMCP-6, PMCP-11 y PMCP-16. Suite total: 119 passed.
**Ficheros generados/afectados**:
- `backend/tests/unit/domain/entities/test_task.py` (reescrito)
- `backend/tests/unit/domain/entities/test_project_entity.py` (nuevo)
- `backend/tests/unit/domain/entities/test_knowledge_entity.py` (nuevo)
- `backend/tests/unit/infrastructure/test_task_classifier.py` (nuevo)
- `backend/tests/unit/adapters/secondary/llm/test_ollama_llm_adapter.py` (nuevo)
- `backend/tests/unit/adapters/secondary/llm/test_claude_adapter.py` (nuevo)

**Prompt**:

```
Pasa los skills de code-reviewer, docs-updater, prompt-librarian, test-writer y
confluence-publisher a todas las épicas desarrolladas hasta el momento:
PMCP-1, PMCP-6, PMCP-11, PMCP-16 y PMCP-21.

Identifica y corrige todos los problemas BLOQUEANTES y DEBE-CORREGIRSE encontrados.
Escribe los tests faltantes para todos los módulos sin cobertura.
```

**Notas**:
- Problemas BLOQUEANTE corregidos: (1) `Task.is_valid_story_points()` y `mark_done()` lanzaban `NotImplementedError`; (2) `chat_ws_handler.py` llamaba directamente a `container.embedding` y `container.vector_store` bypasando la capa de dominio — corregido a `container.rag_service.search()`.
- Problemas DEBE-CORREGIRSE corregidos: (3) `except Exception: pass` silencioso en `chat_ws_handler.py`; (4) CORS `allow_origins=["*"]` hardcodeado → configurable vía `settings.allowed_origins`.
- Para `ClaudeAdapter`: mockear `anthropic.AsyncAnthropic` a nivel de clase (no de instancia) con `patch("anthropic.AsyncAnthropic")` — el patch en el nivel correcto es el módulo donde se importa, no donde se define.
- Para `OllamaLLMAdapter.stream()`: el mock del async context manager de `client.stream()` requiere un objeto separado para el contexto interno (`__aenter__/__aexit__`), distinto del cliente externo.
- `test_task_classifier.py`: verificar case-insensitive (`.lower()` ya está en la implementación).
- Reutilizable en: cualquier sesión de code review cross-épicas — el patrón de audit → correcciones → tests → changelog es el flujo estándar.

---

### 5.5 Tests de integración para PostgreSQL adapters — conftest async con aislamiento por TRUNCATE (PMCP-31)

**Fecha**: 2026-05-04
**Modelo**: claude-sonnet-4-6
**Resultado**: 18 tests de integración en `tests/integration/adapters/` contra PostgreSQL real. Aislamiento por `TRUNCATE CASCADE` entre tests. Cubre ARRAY, filtros, cascade deletes, constraint único de sprint activo.
**Ficheros generados/afectados**:
- `backend/tests/integration/conftest.py`
- `backend/tests/integration/adapters/test_postgresql_task_adapter.py`
- `backend/tests/integration/adapters/test_postgresql_project_adapter.py`

**Prompt** (patrón reutilizable):

```
Escribe tests de integración para PostgreSQLTaskAdapter y PostgreSQLProjectAdapter/SprintAdapter
en tests/integration/adapters/. Requiere PostgreSQL running con schema aplicado (make db-init).

tests/integration/conftest.py:
- session_factory fixture scope=function (fresh engine per test — evita conflictos de event loop)
- clean_db fixture autouse (TRUNCATE projects CASCADE antes de cada test)
- saved_project fixture que crea y persiste un Project de test

TestPostgreSQLTaskAdapter (@pytest.mark.integration):
- test_save_and_retrieve_task: round-trip completo verificando tags=['backend','api']
- test_get_by_id_returns_none_for_missing
- test_list_pending_jira_sync: 2 PENDING + 1 SYNCED → retorna exactamente 2
- test_list_by_project_with_status_filter: 2 DONE + 2 IN_PROGRESS → filtro correcto
- test_delete_task: save + delete + get_by_id retorna None
- test_delete_nonexistent_is_noop: no lanza excepción
- test_save_updates_existing_task: save → modificar → save → verificar cambios persistidos

TestPostgreSQLProjectAdapter (@pytest.mark.integration):
- test_save_and_retrieve_project, test_get_by_id_returns_none_for_missing
- test_list_all_ordered_by_created_at_desc: verificar que dates == sorted(dates, reverse=True)
- test_delete_project, test_delete_cascades_to_tasks

TestPostgreSQLSprintAdapter (@pytest.mark.integration):
- test_save_and_retrieve_sprint
- test_get_active_returns_none_when_no_active_sprint
- test_get_active_returns_active_sprint
- test_save_second_active_sprint_raises_domain_error (pytest.raises(DomainError))
- test_list_by_project, test_get_by_id_returns_none_for_missing
```

**Notas**:
- `scope="function"` para session_factory es obligatorio con pytest-asyncio — los engines con `scope="session"` comparten estado entre event loops de tests distintos causando "cannot perform operation: another operation is in progress".
- `TRUNCATE projects CASCADE` limpia toda la jerarquía FK en una sola operación (projects→sprints→tasks→estimations→chat_sessions).
- Los helpers `_make_task(project_id, **kwargs)` y `_make_sprint(project_id, **kwargs)` locales al módulo de test (no fixtures) hacen cada test autocontenido y más legible.
- `@pytest.mark.integration` permite ejecutar solo tests de integración con `pytest -m integration` y excluirlos en CI con `pytest -m "not integration"`.
- El test `test_save_second_active_sprint_raises_domain_error` verifica la constraint `uq_sprints_one_active_per_project` del DDL — complementa los tests unitarios del adapter.
- Reutilizable en: tests de integración de cualquier adaptador de repositorio SQLAlchemy — el patrón conftest + clean_db + mark es el estándar del proyecto.

---

## 6. Prompts de Documentación

### 6.1 INSTALL.md y RUNBOOK.md — Guías técnicas del proyecto

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: Dos documentos técnicos creados en `docs/` y publicados en Confluence bajo "08. Documentación Técnica del Proyecto". El RUNBOOK incluye 5 problemas conocidos documentados con síntoma, causa y solución.
**Ficheros generados/afectados**: `docs/INSTALL.md`, `docs/RUNBOOK.md`, `scripts/publish_tech_docs.py`

**Prompt**:

```
Crea dos documentos basándote en el estado real del proyecto:

1. docs/INSTALL.md con:
   - Prerrequisitos: Python 3.12+, Node 20+, Docker, Git, Ollama (opcional) con versiones exactas
   - Clonar repo y configurar .env desde .env.example
   - Instalación backend: pip install -e ".[dev]"
   - Instalación frontend: npm install
   - Arranque infraestructura: make up && make db-init
   - Verificación: make verify
   - Instalación Ollama modo local (opcional)

2. docs/RUNBOOK.md con:
   - Comandos diarios del Makefile
   - Flujo de trabajo con Jira y Git flow
   - Cómo ejecutar tests: pytest -m "not integration" y -m integration
   - Cómo actualizar Confluence y Jira: scripts disponibles
   - Problemas conocidos: asyncpg scheme, ChromaDB v2 heartbeat,
     Jira custom fields, Docker WSL2 newgrp

3. Publica ambos en Confluence bajo "08. Documentación Técnica del Proyecto"
```

**Notas**:
- La página padre "08. Documentación Técnica del Proyecto" (id 164045) ya existía — `publish_markdown()` del `ConfluenceClient` la encuentra por título y crea las subpáginas bajo ella.
- Reutilizable: `scripts/publish_tech_docs.py` sirve de plantilla para publicar cualquier par de Markdowns en Confluence con un solo script.

---

## 7. Prompts de Integración

### 7.1 Setup Jira — Crear Proyecto, Épicas e Historias desde Script Python

**Fecha**: 2026-04-28  
**Modelo**: claude-sonnet-4-6  
**Resultado**: Script `scripts/setup_jira.py` que crea el proyecto Jira PMCP (Scrum), 9 épicas y 37 historias del backlog completo del proyecto, con vinculación épica↔historia y ejecución idempotente.  
**Ficheros generados/afectados**: `scripts/setup_jira.py`

**Prompt**:

```
Crea `scripts/setup_jira.py` que:

1. Lee del `.env`: `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`

2. Primero crea el proyecto Jira:
   - Nombre: "PM Copilot"
   - Clave: "PMCP"
   - Tipo: Scrum
   - Lead: el usuario autenticado

3. Luego crea las épicas e historias siguiendo esta estructura exacta:

ÉPICA 1 — Infraestructura base
  - Crear docker-compose con PostgreSQL + ChromaDB
  - DDL de tablas (tasks, projects, sprints, estimations)
  - Crear .env.example completo
  - Script de arranque y verificación del entorno

ÉPICA 2 — LLM Core
  - Implementar ClaudeAdapter (texto + streaming)
  - Implementar LLMRouter con fallback y tenacity
  - Tests unitarios del router
  - Implementar OllamaLLMAdapter para modo local

ÉPICA 3 — Primer caso de uso vertical: EstimateTask
  - Implementar EstimationService en dominio
  - Implementar EstimateTask use case
  - Endpoint REST /estimate funcional
  - Tests de integración del caso de uso

ÉPICA 4 — Chat con streaming
  - Implementar QueryProjectStatus use case
  - WebSocket handler con streaming real
  - useCopilotChat hook en frontend
  - Componente Chat funcional conectado al backend

ÉPICA 5 — RAG y base de conocimiento
  - Implementar OllamaEmbeddingAdapter
  - Implementar ChromaDBAdapter
  - IndexDocuments use case
  - QueryKnowledge use case
  - Tests de integración RAG

ÉPICA 6 — Persistencia
  - Implementar PostgreSQLTaskAdapter
  - Implementar PostgreSQLProjectAdapter + Sprint
  - Migraciones con Alembic
  - Tests de repositorios

ÉPICA 7 — Integraciones externas
  - Implementar JiraAdapter (sync bidireccional)
  - Implementar ConfluenceAdapter (publicar reportes)
  - Implementar GitHubAdapter (leer PRs/commits)
  - SyncJira use case

ÉPICA 8 — Frontend completo
  - Dashboard con métricas del proyecto
  - Página de Tasks conectada al backend
  - Página de Reports con generación bajo demanda
  - PWA: manifest + service worker

ÉPICA 9 — Calidad y despliegue
  - Configurar pytest con cobertura mínima 80%
  - GitHub Actions: CI con tests + lint
  - Dockerfile para backend y frontend
  - Documentación de despliegue en Confluence

4. Cada épica: tipo "Epic", con descripción breve
   Cada historia: tipo "Story", vinculada a su épica con el campo "Epic Link"

5. Al final muestra resumen: épicas creadas, historias creadas, URLs de acceso

Usa `requests` y `python-dotenv`. Añade las dependencias a `requirements-scripts.txt`.
```

**Notas**:
- El script descubre dinámicamente los campos custom de Jira (`customfield_10014` para Epic Link, `customfield_10011` para Epic Name) en lugar de hardcodearlos — funciona en cualquier tenant.
- Estrategia de vinculación en 3 capas: `customfield_10014` → `parent` → Agile API (`/rest/agile/1.0/epic/{key}/issue`). Esto cubre proyectos clásicos, next-gen y configuraciones mixtas.
- La búsqueda de idempotencia usaba `GET /rest/api/3/search` (deprecated desde 2024, error 410). Se corrigió a `GET /rest/api/3/search/jql` en la misma sesión.
- El campo de descripción de épicas requiere formato ADF (Atlassian Document Format), no texto plano — se implementó la función `_adf()` como wrapper.
- Reutilizable en: cualquier proyecto que necesite backlog inicial en Jira. Cambiar el diccionario `BACKLOG` y las constantes `PROJECT_KEY`/`PROJECT_NAME`.
- Variación sugerida: añadir estimación de story points a cada historia en el diccionario `BACKLOG` y pasarla al campo `story_points` en la creación.
- No usar cuando: el proyecto Jira ya tiene issues — la búsqueda por título exacto protege contra duplicados, pero renombrar historias y re-ejecutar sí crearía duplicados.

---

## 8. Prompts de LLM y RAG

### 8.1 Patrón: json_mode en ClaudeAdapter

**Fecha**: 2026-04-30
**Modelo**: claude-sonnet-4-6
**Resultado**: Patrón implementado en `ClaudeAdapter._build_kwargs()` — cuando `LLMRequest.json_mode=True`, se añade instrucción al `system` prompt para forzar output JSON parseable.

**Patrón**:

```python
if request.json_mode:
    json_instruction = "Respond only with valid JSON. Do not include any text outside the JSON."
    system = f"{system}\n{json_instruction}".strip()
```

**Notas**:
- Claude no tiene un parámetro nativo `json_mode` como OpenAI — la instrucción en el system prompt es la forma recomendada.
- El criterio de aceptación es que `json.loads(response.content)` no lance excepción.
- Para validación adicional, usar un `try/except json.JSONDecodeError` en el caso de uso y activar el fallback definido en `DEFINITION_OF_DONE.md`.

---

## 9. Patrones y Buenas Prácticas

### 9.1 Principios para Prompts de Generación de Código

1. **Especifica el contexto arquitectónico**: mencionar siempre el patrón (hexagonal, port/adapter) y la capa donde va el código (dominio, aplicación, adaptador)
2. **Da ejemplos de naming**: los nombres de clases y métodos en el prompt guían el output
3. **Pide type hints siempre**: en Python, solicitar explícitamente type hints completos
4. **Define el comportamiento de error**: especificar qué excepciones lanzar y cuándo
5. **Referencia las interfaces existentes**: si hay un puerto definido, incluirlo en el prompt

### 9.2 Principios para Prompts de Evaluación LLM

1. **Define el golden set antes de escribir el prompt**: los casos de prueba deben existir antes de iterar el prompt
2. **Mide con tasa de aceptación, no con sensación**: registrar ≥ 10 ejecuciones
3. **Versionea los prompts**: cuando un prompt cambia, anotar la versión anterior y la razón del cambio
4. **Prueba los casos límite**: inputs vacíos, inputs muy largos, idiomas mixtos, caracteres especiales

### 9.3 Protocolo de Documentación de Prompt Nuevo

Cuando un prompt produce un resultado significativo:

1. Copiar el prompt completo (sin editar)
2. Añadir a la sección correspondiente en `docs/PROMPTS.md`
3. Documentar: fecha, modelo, resultado, ficheros afectados, notas
4. Si el prompt tiene variaciones que funcionan mejor: documéntarlas en "Notas"
5. Si el prompt falló en algo: documentar la limitación para no repetir el error
