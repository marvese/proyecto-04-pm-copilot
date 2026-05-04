"""publish_docs.py — Publica ADR-001..005, ARCHITECTURE actualizado y páginas técnicas en Confluence."""
import logging
import sys
from pathlib import Path

# Add scripts dir to path so we can import confluence_client
sys.path.insert(0, str(Path(__file__).parent))
from confluence_client import ConfluenceClient  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).parent.parent / "docs"
ARCH_PARENT = "03. Arquitectura y Decisiones Técnicas"
TECH_PARENT = "08. Documentación Técnica del Proyecto"

# ---------------------------------------------------------------------------
# Contenido de las páginas nuevas
# ---------------------------------------------------------------------------

API_REST_MD = """# API REST — PM Copilot

**Versión**: 1.0
**Estado**: Active
**Fecha**: 2026-05-01
**Base URL (local)**: `http://localhost:8000/api/v1`
**Base URL (producción)**: `https://<railway-domain>/api/v1`

---

## Autenticación

Todos los endpoints (excepto `/auth/login` y `/auth/refresh`) requieren el header:

```
Authorization: Bearer <access_token>
```

Los tokens son JWT con expiración configurable via `JWT_EXPIRE_MINUTES`.

---

## Endpoints por módulo

### Auth — `/api/v1/auth`

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/login` | Obtiene access_token + refresh_token con credenciales |
| POST | `/refresh` | Renueva el access_token usando el refresh_token |

**POST /auth/login** — Request body:
```json
{
  "email": "user@example.com",
  "password": "secret"
}
```
Response `200`:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### Projects — `/api/v1/projects`

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `` | Lista todos los proyectos del usuario |
| POST | `` | Crea un nuevo proyecto |
| GET | `/{project_id}` | Obtiene un proyecto por ID |

**GET /projects** — Response `200`:
```json
[
  {
    "id": "uuid",
    "name": "PM Copilot",
    "description": "Asistente PM con RAG",
    "jira_project_key": "PMCP",
    "confluence_space_key": "PBPMIA",
    "github_repo": "org/repo",
    "created_at": "2026-04-24T10:00:00Z"
  }
]
```

---

### Tasks — `/api/v1/projects/{project_id}/tasks`

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `` | Lista tareas del proyecto (filtrables por status, sprint_id) |
| POST | `` | Crea una tarea nueva |
| GET | `/{task_id}` | Obtiene una tarea por ID |
| PATCH | `/{task_id}` | Actualiza campos de una tarea |
| DELETE | `/{task_id}` | Elimina una tarea |
| POST | `/{task_id}/sync-jira` | Sincroniza la tarea con Jira (async, 202) |

**POST /tasks** — Request body:
```json
{
  "title": "Implementar autenticación JWT",
  "description": "Como usuario quiero poder autenticarme...",
  "type": "story",
  "status": "todo",
  "priority": "high",
  "estimated_points": 5,
  "sprint_id": "uuid-opcional",
  "tags": ["auth", "security"]
}
```

Tipos válidos: `story`, `bug`, `task`, `epic`
Status válidos: `backlog`, `todo`, `in_progress`, `in_review`, `done`
Prioridades válidas: `low`, `medium`, `high`, `critical`
Story points válidos (Fibonacci): `1, 2, 3, 5, 8, 13, 21`

---

### Estimation — `/api/v1/projects/{project_id}/estimate`

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `` | Estima story points de una tarea usando LLM + RAG |
| POST | `/breakdown` | Desglosa una épica en historias de usuario |

**POST /estimate** — Request body:
```json
{
  "task_id": "uuid",
  "context": "Contexto adicional opcional"
}
```
Response `200`:
```json
{
  "task_id": "uuid",
  "estimated_points": 5,
  "confidence": 0.82,
  "reasoning": "Basado en tareas similares...",
  "similar_tasks": [...],
  "provider": "claude-sonnet-4-6"
}
```

---

### Sprints — `/api/v1/projects/{project_id}/sprints`

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `` | Lista sprints del proyecto |
| POST | `` | Crea un sprint nuevo |
| GET | `/active` | Devuelve el sprint activo actual (o null) |
| PATCH | `/{sprint_id}` | Actualiza campos de un sprint |

---

### Chat — `/api/v1/chat`

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/sessions` | Crea una nueva sesión de chat |
| GET | `/sessions` | Lista sesiones del usuario |
| POST | `/sessions/{session_id}/messages` | Envía mensaje y obtiene respuesta LLM |
| GET | `/sessions/{session_id}/messages` | Historial de mensajes de una sesión |

**WebSocket** — `ws://localhost:8000/ws/chat/{project_id}`:
Protocolo de mensajes:
```json
// Cliente → Servidor
{"type": "message", "content": "¿Cuántas tareas hay en el sprint activo?"}

// Servidor → Cliente (streaming)
{"type": "token", "content": "Hay "}
{"type": "token", "content": "5 tareas"}
{"type": "done", "content": ""}

// Servidor → Cliente (error)
{"type": "error", "content": "Descripción del error"}
```

---

### Reports — `/api/v1/projects/{project_id}/reports`

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/sprint` | Genera informe de cierre de sprint |
| POST | `/status` | Genera informe de estado del proyecto |
| POST | `/meeting-notes` | Genera acta de reunión |
| GET | `/{report_id}/download/{format}` | Descarga informe (format: `markdown`, `pdf`) |

---

### Knowledge — `/api/v1/projects/{project_id}/knowledge`

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/index` | Indexa documentos de Confluence/Jira/GitHub (async, 202) |
| GET | `/status` | Estado de la indexación (total chunks, last_indexed) |
| POST | `/query` | Búsqueda semántica en la base de conocimiento |

**POST /knowledge/query** — Request body:
```json
{
  "query": "¿Cuál es la arquitectura de autenticación?",
  "top_k": 5
}
```
Response `200`:
```json
{
  "query": "...",
  "chunks": [
    {
      "content": "La autenticación usa JWT...",
      "source": "confluence",
      "source_id": "page-123",
      "score": 0.94
    }
  ],
  "answer": "Basado en la documentación del proyecto..."
}
```

---

## Códigos de respuesta estándar

| Código | Significado |
|--------|-------------|
| 200 | OK — petición procesada correctamente |
| 201 | Created — recurso creado |
| 202 | Accepted — operación async en curso |
| 204 | No Content — eliminación exitosa |
| 400 | Bad Request — payload inválido |
| 401 | Unauthorized — token ausente o inválido |
| 403 | Forbidden — sin permisos para este recurso |
| 404 | Not Found — recurso no encontrado |
| 422 | Unprocessable Entity — validación Pydantic fallida |
| 503 | Service Unavailable — servicio degradado (circuit breaker abierto) |

---

## Documentación interactiva

Con el servidor en local, accesible en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
"""

DATA_MODELS_MD = """# Modelos de Datos — PM Copilot

**Versión**: 1.0
**Estado**: Active
**Fecha**: 2026-05-01

---

## Entidades del Dominio

Las entidades de dominio son Python dataclasses en `backend/src/domain/entities/`. No tienen dependencias externas — solo Python estándar.

---

### Task

```python
@dataclass
class Task:
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str
    type: TaskType            # story | bug | task | epic
    status: TaskStatus        # backlog | todo | in_progress | in_review | done
    priority: TaskPriority    # low | medium | high | critical
    estimated_points: int | None   # Fibonacci: 1,2,3,5,8,13,21
    actual_points: int | None
    sprint_id: uuid.UUID | None
    assignee_id: uuid.UUID | None
    jira_key: str | None           # e.g. "PMCP-42"
    jira_sync_status: JiraSyncStatus  # local_only | pending | synced | failed
    tags: list[str]
    created_at: datetime
    updated_at: datetime
```

**Métodos de dominio**:
- `is_valid_story_points(points: int) -> bool` — valida que el valor es Fibonacci
- `mark_done(actual_points: int) -> None` — cambia status a DONE y registra puntos reales

**Reglas de negocio**:
- `estimated_points` debe ser valor Fibonacci o None
- `jira_sync_status` comienza en `LOCAL_ONLY`; pasa a `SYNCED` tras sincronización exitosa
- Un Task puede existir sin sprint asignado (backlog)

---

### Sprint

```python
@dataclass
class Sprint:
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    goal: str | None
    status: SprintStatus      # planned | active | completed
    capacity_points: int | None
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime
    updated_at: datetime
```

**Métodos de dominio**:
- `is_active() -> bool` — devuelve True si status == ACTIVE

**Reglas de negocio**:
- Solo puede haber un sprint ACTIVE por proyecto en un momento dado
- `capacity_points` es la suma de story points del equipo para el sprint

---

### Project

```python
@dataclass
class Project:
    id: uuid.UUID
    name: str
    description: str
    jira_project_key: str | None    # e.g. "PMCP"
    confluence_space_key: str | None  # e.g. "PBPMIA"
    github_repo: str | None          # e.g. "org/repo"
    created_at: datetime
    updated_at: datetime
```

**Métodos de dominio**:
- `active_sprint(sprints: list[Sprint]) -> Sprint | None` — devuelve el primer sprint activo de la lista

---

### Estimation

```python
@dataclass
class Estimation:
    id: uuid.UUID
    task_id: uuid.UUID
    project_id: uuid.UUID
    estimated_points: int
    confidence: float          # 0.0 - 1.0
    reasoning: str             # explicación del LLM
    similar_tasks: list[dict]  # tareas similares encontradas via RAG
    provider: str              # "claude-sonnet-4-6", "groq/llama3", etc.
    created_at: datetime
```

---

### KnowledgeChunk

```python
@dataclass
class KnowledgeChunk:
    id: uuid.UUID
    project_id: uuid.UUID
    source: KnowledgeSource   # confluence | jira | github | manual
    source_id: str            # ID de la página/issue/PR en origen
    title: str
    content: str              # texto del chunk (max CHUNK_SIZE tokens)
    embedding: list[float] | None  # vector 768-dim (nomic-embed-text)
    chunk_index: int          # índice dentro del documento
    metadata: dict            # metadatos adicionales del origen
    indexed_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

**Método de dominio**:
- `needs_reindex(max_age_hours: int = 24) -> bool` — True si `indexed_at` es None o tiene más de N horas

**Constantes**:
- `CHUNK_SIZE = 512` tokens — tamaño máximo de chunk
- `CHUNK_OVERLAP = 50` tokens — solapamiento entre chunks consecutivos

---

### Report

```python
@dataclass
class Report:
    id: uuid.UUID
    project_id: uuid.UUID
    sprint_id: uuid.UUID | None
    type: ReportType          # sprint_summary | project_status | meeting_notes
    title: str
    content: str              # markdown generado por el LLM
    provider: str
    created_at: datetime
```

---

## Esquema de Base de Datos (PostgreSQL)

Las tablas siguen el modelo de las entidades de dominio, con algunas adiciones para persistencia:

```sql
-- Tabla principal de tareas
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    title TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL CHECK (type IN ('story','bug','task','epic')),
    status TEXT NOT NULL DEFAULT 'todo',
    priority TEXT NOT NULL DEFAULT 'medium',
    estimated_points INTEGER,
    actual_points INTEGER,
    sprint_id UUID REFERENCES sprints(id),
    assignee_id UUID,
    jira_key TEXT,
    jira_sync_status TEXT DEFAULT 'local_only',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices clave
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_sprint_id ON tasks(sprint_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

El DDL completo (7 tablas, índices, triggers) está en `scripts/db_init.sql`.

---

## Vector Store (ChromaDB)

Los `KnowledgeChunk` se almacenan en ChromaDB con la siguiente estructura:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | UUID del chunk |
| `embedding` | float[768] | Vector nomic-embed-text |
| `document` | string | Contenido textual del chunk |
| `metadata.project_id` | string | UUID del proyecto |
| `metadata.source` | string | confluence/jira/github |
| `metadata.source_id` | string | ID en el sistema origen |
| `metadata.title` | string | Título del documento padre |
| `metadata.chunk_index` | int | Posición dentro del documento |

**Colección**: una colección por proyecto, nombrada `project_{project_id}`.

**Búsqueda**: similaridad coseno con `top_k=5` por defecto.

---

## Puertos (Interfaces)

Los puertos son las interfaces abstractas que el dominio define para interactuar con la infraestructura:

| Puerto | Implementación(es) |
|--------|--------------------|
| `TaskRepositoryPort` | `PostgreSQLTaskRepository` |
| `ProjectRepositoryPort` | `PostgreSQLProjectRepository` |
| `VectorStorePort` | `ChromaDBAdapter` |
| `EmbeddingPort` | `OllamaEmbeddingAdapter` |
| `LLMPort` | `LLMRouter` → `ClaudeAdapter` / `OllamaLLMAdapter` |
| `JiraPort` | `JiraAdapter` |
| `ConfluencePort` | `ConfluenceAdapter` |
| `GitHubPort` | `GitHubAdapter` |
"""


def publish_adrs(client: ConfluenceClient) -> None:
    adrs = [
        ("ADR-001 — Stack Tecnológico", "ADR-001-stack.md"),
        ("ADR-002 — Arquitectura Hexagonal vs Microservicios", "ADR-002-hexagonal.md"),
        ("ADR-003 — Circuit Breaker en Integraciones Externas", "ADR-003-circuit-breaker.md"),
        ("ADR-004 — PWA React Primero, Flutter POC Después", "ADR-004-pwa-first.md"),
        ("ADR-005 — LLM Router: Capa de Abstracción LLM", "ADR-005-llm-router.md"),
    ]
    for title, filename in adrs:
        path = DOCS_DIR / filename
        if not path.exists():
            log.error("Fichero no encontrado: %s", path)
            continue
        content = path.read_text(encoding="utf-8")
        result = client.publish_markdown(title, content, parent_title=ARCH_PARENT)
        if result:
            log.info("OK  %s (id=%s)", title, result.get("id"))
        else:
            log.error("FAIL  %s", title)


def publish_architecture(client: ConfluenceClient) -> None:
    path = DOCS_DIR / "ARCHITECTURE.md"
    content = path.read_text(encoding="utf-8")
    result = client.publish_markdown(
        "03. Arquitectura y Decisiones Técnicas",
        content,
        parent_title="00. PM Copilot — Inicio",
    )
    if result:
        log.info("OK  Arquitectura (id=%s)", result.get("id"))
    else:
        log.error("FAIL  Arquitectura")


def publish_tech_docs(client: ConfluenceClient) -> None:
    pages = [
        ("API REST — Referencia de Endpoints", API_REST_MD),
        ("Modelos de Datos — Entidades y Esquema", DATA_MODELS_MD),
    ]
    for title, content in pages:
        result = client.publish_markdown(title, content, parent_title=TECH_PARENT)
        if result:
            log.info("OK  %s (id=%s)", title, result.get("id"))
        else:
            log.error("FAIL  %s", title)


if __name__ == "__main__":
    client = ConfluenceClient.from_env()

    log.info("=== Publicando ADR-001..005 ===")
    publish_adrs(client)

    log.info("=== Actualizando página de Arquitectura ===")
    publish_architecture(client)

    log.info("=== Publicando documentación técnica ===")
    publish_tech_docs(client)

    log.info("=== Listo ===")
