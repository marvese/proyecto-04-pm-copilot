# PM Copilot — Contexto del Proyecto para Claude

## Descripción del Proyecto

**PM Copilot** es un asistente inteligente con RAG (Retrieval-Augmented Generation) diseñado para ayudar a gestionar proyectos de software. Combina LLMs, conocimiento contextual del proyecto y capacidades de integración con herramientas estándar de PM (Confluence, Jira, GitHub).

El objetivo es demostrar una metodología de desarrollo de software con IA donde cada decisión, prompt y aprendizaje queda documentado.

## Stack Tecnológico

### Backend
- **Python 3.12** + **FastAPI** — API REST + WebSocket
- **Arquitectura hexagonal** (Ports & Adapters) — `docs/ADR-002-hexagonal.md`
- **PostgreSQL** — persistencia relacional (Railway en producción)
- **ChromaDB** — vector store para RAG
- **SQLAlchemy** + **Alembic** — ORM y migraciones

### LLM & RAG
- **LLM Router** — capa de abstracción que enruta al LLM apropiado según tipo de tarea y entorno; cuatro adaptadores disponibles:
  - **Anthropic** (Claude Sonnet / Haiku) — calidad máxima; tareas `REASONING` y `GENERATION_LONG`
  - **Groq** (llama3-8b, Mixtral) — velocidad extrema, coste mínimo; tareas `CLASSIFICATION`, `EXTRACTION`, `SIMPLE_QA` en producción
  - **Google Gemini** (Flash, Pro) — alternativa multimodal, tier gratuito generoso; contextos muy largos
  - **Ollama** (llama3, Mistral) — completamente local y gratuito; `LLM_MODE=local` en desarrollo y fallback final
- **nomic-embed-text** via Ollama (`http://localhost:11434`) — embeddings para RAG (independiente del LLM de generación)

### Frontend
- **React 18** + **TypeScript** + **Vite** — SPA/PWA
- **Vercel** — hosting y CI/CD frontend
- **PWA** con Service Workers para capacidades offline básicas

### Integraciones (via adaptadores hexagonales)
- **Confluence** — gestión de documentación del proyecto
- **Jira** — gestión de issues y sprints
- **GitHub** — código, PRs, issues

### Infraestructura
- **Railway** — backend + PostgreSQL + ChromaDB (producción)
- **Docker Compose** — entorno local: `make up` levanta PostgreSQL 16 + ChromaDB; `make db-init` aplica el DDL completo — `docs/ADR-006-infra-local.md`
- **Circuit Breaker** en todas las integraciones externas — `docs/ADR-003-circuit-breaker.md`

## Estructura de Directorios Prevista

```
proyecto-04-pm-copilot/
├── backend/
│   ├── src/
│   │   ├── domain/                    # Núcleo de dominio — sin dependencias externas
│   │   │   ├── entities/              # Entidades del dominio
│   │   │   ├── ports/                 # Interfaces (abstract base classes)
│   │   │   └── services/              # Domain services
│   │   ├── application/               # Casos de uso / command handlers
│   │   │   ├── use_cases/
│   │   │   └── commands/
│   │   ├── adapters/
│   │   │   ├── primary/               # Driving adapters: FastAPI routers, WS handlers
│   │   │   └── secondary/             # Driven adapters: Jira, Confluence, GitHub, DB, LLM
│   │   └── infrastructure/            # Config, DI container, cross-cutting concerns
│   │       ├── llm_router/            # LLM Router + Circuit Breaker
│   │       ├── rag/                   # ChromaDB client, embedding pipeline
│   │       └── config/
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── alembic/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/                  # API clients
│   │   └── types/
│   ├── public/
│   └── package.json
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── FUNCTIONAL_SPEC.md
│   ├── METODOLOGIA.md
│   ├── DEFINITION_OF_DONE.md
│   ├── PROMPTS.md
│   ├── ADR-001-stack.md
│   ├── ADR-002-hexagonal.md
│   ├── ADR-003-circuit-breaker.md
│   ├── ADR-004-pwa-first.md
│   ├── ADR-005-llm-router.md
│   └── ADR-006-infra-local.md
├── scripts/
│   ├── setup_confluence.py                   # Setup inicial del espacio Confluence
│   ├── setup_jira.py                         # Crea proyecto PMCP, 9 épicas y 37 historias en Jira
│   ├── db_init.sql                           # DDL completo (7 tablas, índices, triggers)
│   ├── confluence_client.py                  # Cliente reutilizable Confluence REST API
│   ├── publish_prompts.py                    # Publica PROMPTS.md en Confluence
│   ├── update_jira.py                        # Actualiza issues Jira desde jira_descriptions_complete.json
│   ├── add_task_jira.py                      # Crea un issue Story en Jira con ADF completo
│   ├── jira_descriptions.json                # Backlog: 9 épicas, 37+ historias, estimaciones
│   └── jira_descriptions_complete.json       # Versión con prompts de implementación por historia
├── docker-compose.yml         # PostgreSQL 16 + ChromaDB + pgAdmin (profile "tools")
├── Makefile                   # make up / down / db-init / logs / db-shell / tools-up
├── CLAUDE.md
├── .env
└── .gitignore
```

## Convenciones de Código

### Python (Backend)
- **PEP 8** + type hints obligatorios en todo el código
- Variables y funciones en `snake_case`
- Clases en `PascalCase`
- Puertos (interfaces) con sufijo `Port`: `ProjectRepositoryPort`, `LLMPort`
- Adaptadores con sufijo `Adapter`: `JiraAdapter`, `ConfluenceAdapter`, `ChromaDBAdapter`
- Casos de uso con sufijo `UseCase`: `CreateTaskUseCase`, `EstimateTaskUseCase`
- Commands/DTOs con sufijo `Command` o `Query`
- Tests unitarios en `tests/unit/`, integración en `tests/integration/`

### TypeScript (Frontend)
- **Prettier** + **ESLint** configurados
- Componentes en `PascalCase`
- Hooks con prefijo `use`: `useProjectContext`, `useCopilotChat`
- Tipos e interfaces en `PascalCase`
- Servicios API en `camelCase`: `projectService`, `chatService`

### Commits
- Formato convencional: `<tipo>(<ámbito>): <descripción en imperativo>`
- Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- Ejemplos:
  - `feat(rag): add nomic-embed-text embeddings adapter`
  - `feat(llm-router): implement circuit breaker with tenacity`
  - `docs(adr): add ADR-006 for database migration strategy`

## Reglas de Trabajo

### 1. Biblioteca de Prompts (OBLIGATORIO)
Todo prompt significativo usado durante el desarrollo debe añadirse a `docs/PROMPTS.md` en la sección correspondiente. Un prompt es significativo si:
- Genera código de producción o tests
- Define comportamientos del sistema
- Documenta decisiones de arquitectura
- Podría reutilizarse en el futuro
- Produce documentación de proyecto

**Flujo**: al terminar una sesión de trabajo o al completar una tarea importante, revisar si hay prompts nuevos que añadir a `docs/PROMPTS.md`.

### 2. ADR Obligatorio
Toda decisión arquitectónica relevante requiere un ADR en `docs/`. Formato: `ADR-NNN-descripcion-corta.md`. Usar la plantilla del ADR-001 como referencia.

### 3. Hexagonal Estricto
El módulo `domain/` no puede importar nada de `adapters/` ni de `infrastructure/`. La dependencia fluye hacia adentro: `adapters → application → domain`.

### 4. Circuit Breaker Siempre
Toda llamada a servicios externos (LLMs, Jira, Confluence, GitHub, ChromaDB remoto) debe pasar por un Circuit Breaker. Usar la biblioteca `tenacity` o `circuitbreaker`.

### 5. LLM Router como Único Punto de Acceso a LLMs
Nunca llamar directamente a `anthropic` o `ollama` desde casos de uso. Siempre usar el `LLMRouter` inyectado via puerto.

### 6. Tests antes de Merge
Cada caso de uso nuevo requiere tests unitarios. Los adaptadores requieren tests de integración (contra mocks en CI, opcionales contra servicios reales en local).

### 7. No Determinismo Documentado
Los criterios de aceptación para features LLM deben especificar:
- Umbral mínimo de confianza esperado
- Comportamiento de fallback si el LLM falla o da output inválido
- Método de validación del output
Ver `docs/DEFINITION_OF_DONE.md` para el checklist completo.

## Integraciones Activas

| Servicio | Estado | Config |
|----------|--------|--------|
| PostgreSQL 16 | Activo (local) | `make up` + `make db-init`; `POSTGRES_*` en `.env`; 7 tablas creadas |
| ChromaDB | Activo (local) | `make up`; puerto 8001; `CHROMADB_HOST/PORT` en `.env` |
| Confluence | Activo | `CONFLUENCE_BASE_URL`, espacio `PBPMIA` |
| Anthropic Claude | Activo | `ANTHROPIC_API_KEY` en `.env` |
| Groq | Por configurar | `GROQ_API_KEY` en `.env` — tier gratuito disponible en console.groq.com |
| Google Gemini | Por configurar | `GEMINI_API_KEY` en `.env` — tier gratuito en aistudio.google.com |
| Ollama local | Local | `http://localhost:11434`, modelos: `llama3`, `mistral`, `nomic-embed-text` |
| Jira | Activo | `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` en `.env` — proyecto `PMCP` creado, 9 épicas, 37 historias |
| GitHub | Por configurar | — |
| Railway | Por configurar | — |

## Deuda Técnica Conocida

| ID | Descripción | ADR de referencia |
|----|-------------|------------------|
| DT-001 | Migración a microservicios (trigger: equipo > 3 personas) | `ADR-002-hexagonal.md` |
| DT-002 | Flutter POC — app móvil nativa post-MVP | `ADR-004-pwa-first.md` |
| DT-003 | Benchmark formal de calidad Groq vs Claude vs Gemini por tipo de tarea | `ADR-005-llm-router.md` |
| DT-004 | Evaluar Groq vs Claude Haiku en cost/quality para clasificación | `ADR-005-llm-router.md` |
| DT-005 | Métricas de coste acumulado por proveedor para optimizar routing rules | `ADR-005-llm-router.md` |
| DT-006 | Gemini multimodal para análisis de diagramas de arquitectura | `ADR-005-llm-router.md` |
| DT-007 | Crear `docker-compose.override.yml` al activar Railway para separar config local vs prod | `ADR-006-infra-local.md` |
| DT-008 | Evaluar migrar índices trigram a búsqueda vectorial ChromaDB cuando chunks > 5.000 | `ADR-006-infra-local.md` |

## Skills Activos

Los skills viven en `.claude/skills/` y se invocan con `/nombre-del-skill` o se activan automáticamente según el contexto descrito en cada uno.

| Skill | Cuándo se activa | Fichero |
|-------|-----------------|---------|
| `confluence-publisher` | Tras crear o actualizar documentación significativa (ADRs, lecciones aprendidas, prompts, docs técnica). Invocado desde otros skills como paso final de publicación. | `.claude/skills/confluence-publisher.md` |
| `prompt-librarian` | Cuando se ha usado un prompt significativo durante el desarrollo (genera código, resuelve problema no trivial, produce documentación, es reutilizable). | `.claude/skills/prompt-librarian.md` |
| `docs-updater` | Tras cualquier cambio significativo de arquitectura, dependencias, convenciones o decisiones técnicas. Incluye publicación en Confluence al final. | `.claude/skills/docs-updater.md` |
| `test-writer` | Al crear o modificar cualquier módulo Python en `backend/src/`: entidades, puertos, casos de uso, adaptadores, LLM Router, RAG. | `.claude/skills/test-writer.md` |
| `code-reviewer` | Antes de cerrar cualquier feature o a petición explícita. Verifica arquitectura hexagonal, Circuit Breaker, uso del LLM Router, seguridad y convenciones. | `.claude/skills/code-reviewer.md` |

### Flujo habitual de un skill encadenado

```
Desarrollo de feature
    └── test-writer        (al crear/modificar módulo)
    └── code-reviewer      (al cerrar la feature)
    └── docs-updater       (si hay decisión técnica relevante)
          └── confluence-publisher  (al actualizar docs)
    └── prompt-librarian   (si se usó un prompt significativo)
          └── confluence-publisher  (al actualizar PROMPTS.md)
```

## Referencias Clave

- `docs/PRD.md` — requisitos del producto
- `docs/ARCHITECTURE.md` — arquitectura técnica con diagramas
- `docs/FUNCTIONAL_SPEC.md` — especificación funcional detallada
- `docs/METODOLOGIA.md` — metodología ágil adaptada para desarrollo con IA
- `docs/DEFINITION_OF_DONE.md` — criterios de done para features LLM
- `docs/PROMPTS.md` — biblioteca de prompts del proyecto
