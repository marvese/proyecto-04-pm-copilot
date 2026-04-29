# Arquitectura Técnica — PM Copilot

**Versión**: 0.1  
**Estado**: Draft  
**Fecha**: 2026-04-24  

---

## 1. Visión General

PM Copilot implementa **arquitectura hexagonal** (Ports & Adapters) con un núcleo de dominio aislado rodeado de adaptadores intercambiables. Esta elección facilita el testing, la evolución independiente de integraciones y la migración futura a microservicios.

Ver decisión completa en `docs/ADR-002-hexagonal.md`.

---

## 2. Diagrama de Arquitectura

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                            INFRASTRUCTURE LAYER                                  ║
║                                                                                  ║
║  ┌─────────────────┐    ┌──────────────────────────────────────────────────────┐ ║
║  │  DRIVING SIDE   │    │               DRIVEN SIDE                            │ ║
║  │  (Primary)      │    │               (Secondary)                            │ ║
║  └─────────────────┘    └──────────────────────────────────────────────────────┘ ║
║                                                                                  ║
║  ┌──────────────┐        ┌───────────────────────────────────────────────────┐  ║
║  │  React PWA   │        │                LLM ROUTER                         │  ║
║  │  (Vercel)    │──────▶ │  ┌────────────────────┐  ┌─────────────────────┐  │  ║
║  └──────────────┘  HTTP  │  │  Claude Sonnet/Haiku│  │  Ollama / llama3    │  │  ║
║                   /WS    │  │  (tareas complejas) │  │  (tareas simples)   │  │  ║
║  ┌──────────────┐        │  └────────────────────┘  └─────────────────────┘  │  ║
║  │  CLI Scripts │──────▶ │  Circuit Breaker + Routing Logic                  │  ║
║  └──────────────┘        └───────────────────────────────────────────────────┘  ║
║          │                                                                       ║
║          │               ┌───────────────────────────────────────────────────┐  ║
║          │               │                  RAG ENGINE                        │  ║
║          │               │  ┌─────────────┐      ┌──────────────────────┐   │  ║
║          │               │  │  ChromaDB   │      │  nomic-embed-text    │   │  ║
║          │               │  │  (vector    │      │  (via Ollama local)  │   │  ║
║          │               │  │   store)    │      └──────────────────────┘   │  ║
║          │               │  └─────────────┘                                 │  ║
║          │               └───────────────────────────────────────────────────┘  ║
║          │                                                                       ║
║  ╔═══════▼══════════════════════════════════════════════════════════════════╗   ║
║  ║                         PRIMARY ADAPTERS                                 ║   ║
║  ║  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐    ║   ║
║  ║  │  FastAPI Router  │  │  WebSocket       │  │  Background Tasks  │    ║   ║
║  ║  │  (REST API)      │  │  (streaming)     │  │  (Celery / ARQ)    │    ║   ║
║  ║  └────────┬─────────┘  └────────┬─────────┘  └─────────┬──────────┘    ║   ║
║  ╚═══════════╪════════════════════╪═══════════════════════╪═══════════════╝   ║
║              │                    │                        │                    ║
║  ╔═══════════▼════════════════════▼════════════════════════▼═══════════════╗   ║
║  ║                        APPLICATION LAYER                                 ║   ║
║  ║                         (Use Cases)                                      ║   ║
║  ║  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐    ║   ║
║  ║  │EstimateTaskUC  │  │CreateTaskUC    │  │GenerateReportUC        │    ║   ║
║  ║  │PlanSprintUC    │  │SyncJiraUC      │  │QueryProjectStatusUC    │    ║   ║
║  ║  │QueryKnowledge  │  │UpdateTaskUC    │  │IndexDocumentsUC        │    ║   ║
║  ║  └────────┬───────┘  └───────┬────────┘  └────────────┬───────────┘    ║   ║
║  ╚═══════════╪══════════════════╪═════════════════════════╪════════════════╝   ║
║              │                  │                          │                    ║
║  ╔═══════════▼══════════════════▼══════════════════════════▼════════════════╗  ║
║  ║                           DOMAIN CORE                                    ║  ║
║  ║                                                                           ║  ║
║  ║  ┌─────────────────────────────────────────────────────────────────┐    ║  ║
║  ║  │                          ENTITIES                               │    ║  ║
║  ║  │  Project │ Sprint │ Task │ Estimation │ Report │ KnowledgeChunk │    ║  ║
║  ║  └─────────────────────────────────────────────────────────────────┘    ║  ║
║  ║                                                                           ║  ║
║  ║  ┌─────────────────────────────────────────────────────────────────┐    ║  ║
║  ║  │                     PORTS (Interfaces)                          │    ║  ║
║  ║  │  TaskRepositoryPort │ LLMPort │ EmbeddingPort │ VectorStorePort │    ║  ║
║  ║  │  JiraPort │ ConfluencePort │ GitHubPort │ DocumentGeneratorPort │    ║  ║
║  ║  └─────────────────────────────────────────────────────────────────┘    ║  ║
║  ║                                                                           ║  ║
║  ║  ┌─────────────────────────────────────────────────────────────────┐    ║  ║
║  ║  │                    DOMAIN SERVICES                              │    ║  ║
║  ║  │  EstimationService │ PlanningService │ RAGService               │    ║  ║
║  ║  └─────────────────────────────────────────────────────────────────┘    ║  ║
║  ╚═══════════════════════════════════════════════════════════════════════════╝  ║
║              │                  │                          │                    ║
║  ╔═══════════▼══════════════════▼══════════════════════════▼════════════════╗  ║
║  ║                      SECONDARY ADAPTERS                                  ║  ║
║  ║  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ║  ║
║  ║  │PostgreSQL│  │ChromaDB  │  │  Jira    │  │Confluence│  │  GitHub  │  ║  ║
║  ║  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │  ║  ║
║  ║  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  ║  ║
║  ╚═══════╪═════════════╪═════════════╪══════════════╪═════════════╪════════╝  ║
║          │             │             │              │             │            ║
║  ┌───────▼──┐  ┌───────▼──┐  ┌──────▼──────┐ ┌────▼──────┐ ┌───▼──────┐   ║
║  │PostgreSQL│  │ ChromaDB │  │  Jira API   │ │Confluence │ │ GitHub   │   ║
║  │(Railway) │  │(Railway) │  │  (Atlassian)│ │  API      │ │  API     │   ║
║  └──────────┘  └──────────┘  └─────────────┘ └───────────┘ └──────────┘   ║
║                                                                                  ║
║  ════════════════════ CROSS-CUTTING CONCERNS ════════════════════               ║
║  Circuit Breaker │ Structured Logging │ Auth/JWT │ Config │ Error Handling      ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. Capas de la Arquitectura

### 3.1 Domain Core

El núcleo de dominio es independiente de cualquier framework o tecnología externa. Contiene:

- **Entities**: objetos de negocio con identidad e invariantes (`Task`, `Sprint`, `Estimation`, `Project`, `KnowledgeChunk`)
- **Ports**: interfaces abstractas que definen lo que el dominio necesita del exterior (`LLMPort`, `TaskRepositoryPort`, `VectorStorePort`)
- **Domain Services**: lógica de negocio que no pertenece a una sola entidad (`EstimationService` que coordina historial + LLM + complejidad)

**Regla clave**: el dominio nunca importa nada de `adapters/` ni de `infrastructure/`. Solo Python estándar y otras entidades de dominio.

### 3.2 Application Layer

Orquesta los casos de uso. Cada caso de uso:
- Recibe un `Command` o `Query` (DTO)
- Usa puertos inyectados para acceder a repositorios, LLMs, etc.
- Retorna un resultado tipado
- Es completamente testeable con mocks de los puertos

```
EstimateTaskUseCase(
    llm_port: LLMPort,
    task_repo: TaskRepositoryPort,
    vector_store: VectorStorePort
)
```

### 3.3 Primary Adapters (Driving)

Traducen el mundo exterior al dominio:
- **FastAPI Routers**: reciben HTTP requests, validan con Pydantic, llaman a use cases
- **WebSocket Handler**: streaming de respuestas del LLM al frontend
- **Background Task Runner**: indexación de documentos, sincronización periódica

### 3.4 Secondary Adapters (Driven)

Implementan los puertos del dominio para servicios externos:
- **PostgreSQLAdapter**: implementa `TaskRepositoryPort`, `ProjectRepositoryPort`
- **ChromaDBAdapter**: implementa `VectorStorePort`
- **OllamaEmbeddingAdapter**: implementa `EmbeddingPort` usando `nomic-embed-text`
- **JiraAdapter**: implementa `JiraPort` con Circuit Breaker
- **ConfluenceAdapter**: implementa `ConfluencePort` con Circuit Breaker
- **GitHubAdapter**: implementa `GitHubPort` con Circuit Breaker
- **ClaudeAdapter** / **OllamaLLMAdapter**: implementan `LLMPort`

### 3.5 LLM Router

Componente cross-cutting que implementa `LLMPort` enrutando al proveedor apropiado:

```
LLMRouter
  ├── task_classifier: determina LLMTaskType de la tarea
  ├── claude_adapter: REASONING, GENERATION_LONG — calidad máxima (Anthropic)
  ├── groq_adapter: CLASSIFICATION, EXTRACTION, SIMPLE_QA — velocidad máxima
  ├── gemini_adapter: contextos muy largos, alternativa multimodal
  ├── ollama_adapter: LLM_MODE=local y fallback final — sin coste
  └── circuit_breaker: fallback automático entre proveedores (tenacity)
```

Ver `docs/ADR-005-llm-router.md` para la lógica de routing.

### 3.6 RAG Engine

Pipeline de recuperación y generación aumentada:

```
Indexación:
  Documento → Chunking → nomic-embed-text → ChromaDB

Recuperación:
  Query → nomic-embed-text → ChromaDB similarity search → Top-K chunks → Context

Generación:
  Prompt + Context → LLM Router → Respuesta fundamentada
```

---

## 4. Flujo de Datos: Caso de Uso "Estimar Tarea"

```
Usuario (PWA)
    │
    │ POST /api/v1/tasks/estimate {description, context}
    ▼
FastAPI Router (Primary Adapter)
    │ Valida input con Pydantic
    │ Crea EstimateTaskCommand
    ▼
EstimateTaskUseCase (Application)
    │ 1. Busca tareas similares en VectorStore
    │ 2. Recupera velocidad histórica del sprint
    │ 3. Construye prompt con contexto RAG
    ▼
LLM Router (Infrastructure)
    │ Clasifica: tarea compleja → Claude Sonnet
    │ Aplica Circuit Breaker
    ▼
Claude API / Ollama (External)
    │ Genera estimación estructurada
    ▼
EstimateTaskUseCase
    │ Valida output (JSON schema)
    │ Persiste estimación en PostgreSQL
    ▼
FastAPI Router
    │ Retorna EstimationResponse
    ▼
React PWA
```

---

## 5. Diagrama de Despliegue

```
┌─────────────────────────────────────────────────────────────────────┐
│                           PRODUCCIÓN                                 │
│                                                                       │
│  ┌─────────────────┐         ┌──────────────────────────────────┐   │
│  │     Vercel      │         │            Railway               │   │
│  │                 │         │                                  │   │
│  │  React PWA      │──HTTPS─▶│  FastAPI Container               │   │
│  │  (CDN global)   │         │  ├── PostgreSQL (managed)        │   │
│  │                 │         │  └── ChromaDB Container          │   │
│  └─────────────────┘         └──────────────────────────────────┘   │
│                                           │                          │
│                               ┌───────────▼──────────────────────┐  │
│                               │    External Services (Atlassian)  │  │
│                               │  Jira API │ Confluence API        │  │
│                               └───────────────────────────────────┘  │
│                                           │                          │
│                               ┌───────────▼──────────────────────┐  │
│                               │      Anthropic API               │  │
│                               │  Claude Sonnet / Haiku           │  │
│                               └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          DESARROLLO LOCAL                            │
│                                                                       │
│  React (Vite dev)     FastAPI (uvicorn)     Ollama                   │
│  localhost:5173  ──▶  localhost:8000   ──▶  localhost:11434          │
│                            │                                          │
│                       PostgreSQL           ChromaDB                  │
│                       localhost:5432       localhost:8001             │
│                       (Docker)             (Docker)                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Decisiones Arquitectónicas

| Decisión | ADR |
|----------|-----|
| Stack tecnológico | `ADR-001-stack.md` |
| Hexagonal vs microservicios | `ADR-002-hexagonal.md` |
| Circuit Breaker en integraciones | `ADR-003-circuit-breaker.md` |
| PWA React primero, Flutter después | `ADR-004-pwa-first.md` |
| LLM Router y embeddings | `ADR-005-llm-router.md` |
| Infraestructura de desarrollo local | `ADR-006-infra-local.md` |
