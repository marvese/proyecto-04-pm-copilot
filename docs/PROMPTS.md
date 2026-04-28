# Biblioteca de Prompts — PM Copilot

**Versión**: 0.1  
**Fecha**: 2026-04-24  

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

## 4. Prompts de Desarrollo Frontend

*[Añadir prompts de desarrollo frontend aquí]*

---

## 5. Prompts de Testing

*[Añadir prompts de testing aquí]*

---

## 6. Prompts de Documentación

*[Añadir prompts de documentación aquí]*

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

*[Añadir prompts relacionados con LLM Router, RAG pipeline, embeddings aquí]*

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
