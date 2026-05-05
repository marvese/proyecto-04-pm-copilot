---
title: "04. Lecciones Aprendidas"
parent: "00. PM Copilot — Inicio"
---

# 04. Lecciones Aprendidas

Compilación de lecciones aprendidas, errores cometidos y buenas prácticas identificadas a lo largo del proyecto. Actualizado al final de cada sprint.

---

## Épica 1 — Infraestructura base

### asyncpg requiere scheme `postgresql://` no `postgresql+asyncpg://`

**Problema:** Al conectar asyncpg directamente sin SQLAlchemy, el scheme `postgresql+asyncpg://` falla. Es específico de SQLAlchemy.

**Solución:** Usar `postgresql://` o `postgres://` para asyncpg puro. Mantener dos variables si usas ambas librerías: `DATABASE_URL` para asyncpg y `SQLALCHEMY_DATABASE_URL` para Alembic.

---

### ChromaDB v2 usa `/api/v2/heartbeat`, no `/api/v1/heartbeat`

**Problema:** `verify_env.py` fallaba al verificar ChromaDB porque usaba el endpoint de la v1. ChromaDB latest ya es v2 y cambió la ruta del heartbeat.

**Lección:** Siempre verificar la versión del servicio antes de asumir rutas de API. Considerar fijar la versión de imagen en `docker-compose.yml` para mayor estabilidad.

---

### Docker en WSL2: permisos de grupo

**Problema:** `make up` fallaba en WSL2 con error de permisos del Docker socket.

**Solución:** Ejecutar `newgrp docker` en el terminal o cerrar y reabrir la sesión WSL2.

**Lección:** Documentar esto en el RUNBOOK desde el inicio.

---

### Jira Cloud usa custom fields no estándar

Los custom fields de Story Points y Epic Link varían entre instancias de Jira Cloud. En este proyecto:

| Campo | Field ID estándar | Field ID real en PMCP |
|---|---|---|
| Story Points | customfield_10016 | customfield_10032 |
| Epic Link | customfield_10014 | customfield_10014 ✓ |

**Lección:** Siempre autodescubrir campos via `GET /rest/api/3/field`. Guardar en `.env` como `JIRA_FIELD_STORY_POINTS` y `JIRA_FIELD_EPIC_LINK`.

---

### `.gitignore` debe incluir `__pycache__` desde el inicio

**Problema:** Al ejecutar pytest por primera vez, ficheros `*.pyc` y `__pycache__` se colaron en el índice de Git.

**Solución:**
```bash
git rm -r --cached **/__pycache__/
git rm -r --cached **/*.pyc
```

**Lección:** Crear el `.gitignore` completo antes del primer commit. Incluir siempre: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.coverage`, `htmlcov/`, `.env`.

---

## Épica 2 — LLM Core

### `RuntimeError("unreachable")` sin cubrir en tests es correcto

El `LLMRouter` tiene 98% de cobertura en lugar de 100%. La línea no cubierta es un `raise RuntimeError("unreachable")` intencional.

**Lección:** Un `RuntimeError("unreachable")` es una guardia defensiva por diseño. Si el código llegara ahí significaría un bug. Usar `# pragma: no cover` si el porcentaje mínimo es estricto.

---

### Usar `AsyncAnthropic` en lugar del cliente síncrono

**Lección:** En FastAPI todo debe ser async. Nunca usar clientes síncronos de APIs externas en handlers async — bloquean el event loop. El `ClaudeAdapter` usa `AsyncAnthropic` con `async with client.messages.stream()`.

---

## Épica 3 — EstimateTask

### Respuestas JSON del LLM requieren validación defensiva

Claude puede devolver JSON válido pero con valores fuera del rango esperado (`confidence` > 1.0, `points` no Fibonacci).

**Lección:** Siempre validar la respuesta del LLM con Pydantic antes de persistir. Añadir fallbacks razonables cuando los valores están fuera de rango.

---

## Épica 4 — Chat con streaming

### WebSocket requiere gestión explícita del ciclo de vida en React

**Problema:** El hook `useCopilotChat` abría conexiones WebSocket que no se cerraban al desmontar el componente, causando memory leaks.

**Solución:** Implementar cleanup en `useEffect`:
```typescript
return () => ws.close();
```

**Lección:** Usar `useReducer` en lugar de múltiples `useState` para evitar stale closures en los callbacks del WebSocket.

---

## Épica 5 — RAG

### ChromaDB requiere filtros por `project_id` en todas las queries

Sin filtrar por `project_id` en los metadatos, las búsquedas devuelven chunks de proyectos distintos.

**Lección:** Definir la estrategia de naming de colecciones y filtros de metadatos desde el inicio del diseño del RAG.

---

## Sistema de sincronización diferida de documentación

**Problema identificado:** Usar Claude Code o Claude.ai con el conector Atlassian Rovo para actualizar Jira y Confluence consume tokens innecesariamente. El contexto de Claude Code debe reservarse para implementación de código.

**Solución implementada:** Sistema de sincronización diferida en dos fases:

Fase 1 — Durante la sesión de Claude Code (cero tokens de API):
- Claude Code genera ficheros .md en docs/pending/confluence/
- Claude Code genera docs/pending/jira/update-tasks.json
- Sin llamadas a APIs externas

Fase 2 — Al cerrar la sesión (desde terminal):
- make sync-all ejecuta sync_confluence.py + sync_jira_status.py
- Los ficheros procesados se mueven a docs/published/ con timestamp

**Estructura de carpetas:**
```
docs/
  pending/
    confluence/   → .md pendientes de subir a Confluence
    jira/         → update-tasks.json pendiente de sincronizar
  published/      → ficheros procesados con timestamp
```

**Comandos:**
```bash
make sync-docs   → sube docs/pending/confluence/ a Confluence
make sync-jira   → actualiza estado de tareas en Jira
make sync-all    → ambos en secuencia
```

**Lección:** Separar la generación de contenido (Claude Code, sin coste de API) de la sincronización (scripts locales, sin LLM) reduce el consumo de tokens y desacopla el flujo de desarrollo de las APIs externas.

---

## Buenas prácticas identificadas

### Usar el skill `session-start.md` al inicio de cada sesión
Claude Code pierde el contexto entre sesiones. El skill en `.claude/skills/session-start.md` carga automáticamente el contexto del proyecto al leer `CLAUDE.md`. Invocación: `Lee y ejecuta .claude/skills/session-start.md`.

### Un prompt bien definido ahorra iteraciones
Las tareas con prompt detallado en `jira_descriptions_complete.json` (contexto + instrucción exacta) se completan en 1-2 iteraciones. Las tareas sin prompt definido requieren 3-5 iteraciones.

### Commits atómicos por tarea de Jira
Un commit por tarea con el key de Jira en el mensaje (`feat(PMCP-7): ...`) facilita la trazabilidad entre código y backlog. Evitar commits acumulativos de varias tareas.

### Verificar el entorno antes de cada sesión
`make verify` detecta problemas de configuración antes de empezar a desarrollar. Evita perder tiempo depurando errores de conexión.

### División de responsabilidades por herramienta

| Tarea | Herramienta |
|---|---|
| Implementar código, tests, commits | Claude Code |
| Actualizar Confluence | `make sync-docs` o Claude.ai |
| Marcar tareas Done en Jira | `make sync-jira` o UI de Jira |
| Planificación, revisión de calidad | Claude.ai (este chat) |

### Ratio vibe coding vs desarrollo humano: ~3.4×
Estimación inicial del proyecto: 37.8h con Claude Code vs 127.0h para un senior sin IA. Se actualizará con datos reales al completar el proyecto.
