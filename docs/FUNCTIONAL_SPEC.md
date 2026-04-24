# Especificación Funcional — PM Copilot

**Versión**: 0.1  
**Estado**: Draft  
**Fecha**: 2026-04-24  

---

## 1. Módulo de Chat Conversacional

### 1.1 Chat con Contexto de Proyecto

**Descripción**: interfaz conversacional principal donde el usuario interactúa con el copilot en lenguaje natural. El sistema mantiene contexto de la conversación y enriquece las respuestas con RAG sobre el conocimiento del proyecto.

**Flujo principal**:
1. Usuario envía mensaje de texto
2. Sistema clasifica la intención (ver §1.2)
3. Si la intención requiere datos del proyecto: ejecuta RAG query sobre ChromaDB
4. Construye prompt con contexto RAG + historial de conversación
5. Envía al LLM Router (streaming)
6. Retorna respuesta con fuentes citadas

**Respuestas en streaming**: el frontend recibe tokens via WebSocket y los renderiza progresivamente.

**Historial de conversación**: se mantiene en sesión (server-side, PostgreSQL). El usuario puede iniciar nueva conversación. El LLM recibe los últimos N turnos como contexto (N configurable, default 10).

**API**:
```
POST /api/v1/chat/messages
Body: { session_id: uuid, content: string }
Response: { message_id: uuid, stream_url: string }

GET /api/v1/chat/sessions/{session_id}/messages
Response: Message[]

WebSocket /api/v1/chat/stream/{message_id}
Events: { type: "token", content: string } | { type: "done", sources: Source[] } | { type: "error", detail: string }
```

---

### 1.2 Clasificación de Intenciones

El sistema reconoce las siguientes intenciones implícitas y comandos explícitos:

| Intención | Comando explícito | Descripción |
|-----------|------------------|-------------|
| Estimación | `/estimate <descripción>` | Estimar historia/tarea |
| Crear tarea | `/task <descripción>` | Crear tarea en el sistema |
| Generar informe | `/report sprint` `/report status` | Generar informe |
| Consultar estado | `/status` | Estado actual del proyecto |
| Query de conocimiento | (natural language) | RAG sobre documentación |
| Desglosar epic | `/breakdown <descripción>` | Descomponer en historias |
| Planificar sprint | `/plan sprint` | Asistir en planning |

Los comandos explícitos garantizan routing determinista. El lenguaje natural pasa por el clasificador.

---

## 2. Módulo de Estimación

### 2.1 Estimar Historia de Usuario

**Entrada**: descripción de la historia, criterios de aceptación opcionales, etiquetas de componente.

**Proceso**:
1. Embedding de la descripción con `nomic-embed-text`
2. Búsqueda de historias similares en ChromaDB (top-5 por similitud coseno)
3. Recuperación de estimaciones reales vs estimadas de esas historias
4. Construcción de prompt con: descripción, contexto RAG, velocidad del equipo, complejidad del componente
5. LLM genera estimación estructurada

**Output**:
```json
{
  "points": 5,
  "confidence": 0.72,
  "breakdown": {
    "frontend": 2,
    "backend": 2,
    "testing": 1
  },
  "rationale": "Similar a 'Implementar autenticación JWT' (5 puntos, completada en sprint 3)...",
  "similar_tasks": [
    { "id": "uuid", "title": "...", "estimated": 5, "actual": 6 }
  ],
  "risks": ["Dependencia de API de Jira no documentada"]
}
```

**Validación**: el output se valida contra JSON schema. Si el LLM devuelve output inválido: retry (1x), luego error 422.

**Rango válido de puntos**: 1, 2, 3, 5, 8, 13, 21 (Fibonacci). El LLM debe elegir de esta escala.

---

### 2.2 Descomponer Epic en Historias

**Entrada**: descripción del epic, contexto adicional opcional.

**Output**: lista de historias de usuario con formato `Como [rol], quiero [acción], para [beneficio]`, cada una con estimación tentativa.

**Límite**: máximo 15 historias por epic.

---

### 2.3 Planificación de Sprint

**Entrada**: backlog priorizado (ids de tareas), capacidad del equipo (puntos disponibles).

**Output**: selección de tareas para el sprint con justificación, riesgos identificados y tareas que quedan fuera con razón.

---

## 3. Módulo de Tareas

### 3.1 Modelo de Datos de Tarea

```
Task {
  id: uuid
  project_id: uuid
  title: string
  description: string (markdown)
  type: "story" | "bug" | "task" | "epic"
  status: "backlog" | "todo" | "in_progress" | "in_review" | "done"
  priority: "low" | "medium" | "high" | "critical"
  estimated_points: int | null
  actual_points: int | null
  sprint_id: uuid | null
  assignee_id: uuid | null
  jira_key: string | null       # "PROJ-123" si sincronizado
  jira_sync_status: "pending" | "synced" | "failed" | "local_only"
  tags: string[]
  created_at: datetime
  updated_at: datetime
}
```

### 3.2 CRUD de Tareas via Chat

El usuario puede crear, actualizar y consultar tareas mediante lenguaje natural:

- "Crea una tarea: implementar endpoint de estimación, alta prioridad, 5 puntos"
- "Cierra la tarea 42 y añade la nota: se resolvió usando el adaptador de Jira existente"
- "¿Qué tareas están bloqueadas esta semana?"
- "Asigna la tarea 15 a Juan y muévela a In Review"

### 3.3 Sincronización con Jira

**Sincronización**: pull periódica (configurable, default cada 15 min) + push inmediato al crear/actualizar tarea.

**Conflictos**: si una tarea fue modificada en Jira y en local simultáneamente, la versión de Jira prevalece con log de advertencia.

**Estados de sincronización**:
- `synced`: tarea existe en Jira y está al día
- `pending`: cambio local pendiente de push a Jira
- `failed`: fallo en sync, requiere intervención manual
- `local_only`: tarea creada localmente, aún no enviada a Jira (por decisión explícita o Circuit Breaker abierto)

---

## 4. Módulo de Informes

### 4.1 Informe de Estado de Sprint

**Trigger**: comando `/report sprint` o solicitud natural.

**Contenido del informe**:
- Resumen ejecutivo (2-3 párrafos)
- Métricas: puntos completados, puntos restantes, velocidad, burn-down
- Tareas completadas con puntos
- Tareas en progreso con estado y posibles bloqueadores
- Riesgos identificados
- Acciones recomendadas

**Formatos de exportación**:
- Markdown (por defecto, renderizado en el chat)
- DOCX (via `python-docx`)
- Página de Confluence (via API de Confluence)

### 4.2 Informe de Estado del Proyecto

Visión de más alto nivel: objetivos del sprint actual, avance hacia el milestone, hitos próximos, métricas de salud del proyecto.

### 4.3 Acta de Reunión

**Entrada**: notas o transcripción de la reunión (texto libre).

**Output**: acta estructurada con:
- Asistentes (si se mencionan)
- Puntos discutidos
- Decisiones tomadas
- Acciones con responsable y fecha (si se mencionan)
- Próxima reunión (si se menciona)

---

## 5. Módulo de Conocimiento (RAG)

### 5.1 Fuentes de Conocimiento Indexadas

| Fuente | Frecuencia de indexación | Scope |
|--------|-------------------------|-------|
| Confluence (espacio PBPMIA) | Diaria + on-demand | Todas las páginas del espacio |
| Jira issues (proyecto activo) | Cada 4 horas | Issues de los últimos 6 meses |
| GitHub (repo del proyecto) | Por webhook en PR/commit | PRs, issues, README, ADRs |
| Conversaciones pasadas | Continua | Resúmenes de sesiones marcadas como relevantes |

### 5.2 Chunking Strategy

- Tamaño de chunk: 512 tokens con overlap de 50 tokens
- Splitting por secciones de Markdown (preferido) o por tamaño fijo
- Metadata por chunk: `source`, `document_id`, `section`, `last_updated`, `url`

### 5.3 Queries de Conocimiento

Las queries en lenguaje natural sobre documentación del proyecto pasan por:
1. Clasificación: ¿es una query de conocimiento?
2. Embedding de la query
3. Similarity search en ChromaDB (top-5)
4. Generación de respuesta con LLM + chunks como contexto
5. La respuesta incluye citas con links a la fuente original

---

## 6. Dashboard de Proyecto

### 6.1 Vista Principal

- Estado del sprint activo: puntos completados / total, días restantes
- Tareas por estado (Kanban summary)
- Últimas actividades (feed)
- Alertas activas (bloqueadores, tareas retrasadas)
- Acceso rápido al chat

### 6.2 Métricas de Velocidad

- Velocidad por sprint (últimos 5 sprints)
- Tendencia: ¿el equipo está acelerando o ralentizando?
- Comparación estimado vs real por sprint

---

## 7. Gestión de Sesiones y Autenticación

**MVP**: autenticación simple via JWT (email/password). Sin OAuth en MVP.

**Sesiones de chat**: persistidas en PostgreSQL. El usuario puede acceder al historial de conversaciones anteriores.

**Proyectos**: un usuario puede tener múltiples proyectos. El contexto RAG es por proyecto.

---

## 8. API Endpoints de Alto Nivel

```
# Auth
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh

# Proyectos
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{id}

# Chat
POST   /api/v1/chat/sessions
GET    /api/v1/chat/sessions
POST   /api/v1/chat/sessions/{id}/messages
WS     /api/v1/chat/stream/{message_id}

# Tareas
GET    /api/v1/tasks
POST   /api/v1/tasks
GET    /api/v1/tasks/{id}
PATCH  /api/v1/tasks/{id}
DELETE /api/v1/tasks/{id}
POST   /api/v1/tasks/{id}/sync-jira

# Estimación
POST   /api/v1/estimate
POST   /api/v1/estimate/breakdown

# Informes
POST   /api/v1/reports/sprint
POST   /api/v1/reports/status
POST   /api/v1/reports/meeting-notes
GET    /api/v1/reports/{id}/download/{format}

# Conocimiento
POST   /api/v1/knowledge/index
GET    /api/v1/knowledge/status
POST   /api/v1/knowledge/query

# Sprints
GET    /api/v1/sprints
POST   /api/v1/sprints
GET    /api/v1/sprints/active
PATCH  /api/v1/sprints/{id}
```
