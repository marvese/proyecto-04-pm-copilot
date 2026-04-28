# ADR-006 — Infraestructura de desarrollo local: Docker Compose + DDL Schema

**Estado**: Aceptado  
**Fecha**: 2026-04-28

## Contexto

El proyecto necesita un entorno local reproducible que levante PostgreSQL y ChromaDB sin depender de instalaciones en el host ni de credenciales de Railway. Además, el schema de la base de datos requiere decisiones explícitas sobre tipos de columna, índices y constraints que impactan en rendimiento, portabilidad y mantenimiento a largo plazo.

## Opciones consideradas

### Gestión del entorno local

| Opción | Pros | Contras |
|--------|------|---------|
| **Docker Compose** | Un comando (`make up`), reproducible, sin instalar nada en el host, compose file como documentación viva | Requiere Docker Desktop o Engine instalado |
| Bare metal (instalar PostgreSQL/ChromaDB directamente) | Sin overhead de contenedores | No reproducible entre máquinas, conflictos de versión |
| Dev containers (VS Code) | Entorno completo en contenedor | Complejidad adicional, innecesaria en equipo de 1 persona |

### Tipos de PK

| Opción | Pros | Contras |
|--------|------|---------|
| **UUID v4 (`gen_random_uuid()`)** | Sin colisiones en entornos distribuidos, opaco (no revela volumen), nativo en PG 16 sin extensión | Índices ~20 % más grandes que BIGINT, inserts levemente más lentos |
| `BIGSERIAL` / `IDENTITY` | Compacto, indexing eficiente | Revela volumen, problemático en sharding futuro, no portable entre instancias |

### Enums de columna

| Opción | Pros | Contras |
|--------|------|---------|
| **`VARCHAR + CHECK`** | Añadir valores sin `ALTER TYPE`, sin lock en tabla | Sin type-safety a nivel motor |
| `CREATE TYPE` enum | Type-safety, autodocumentado | `ALTER TYPE ADD VALUE` requiere transacción no cancelable en PG < 12; aún así requiere migraciones |

### Full-text search

| Opción | Pros | Contras |
|--------|------|---------|
| **GIN + `pg_trgm`** | Búsqueda por substring/similitud sin normalización, ya incluido en PG | No reemplaza búsqueda semántica (para eso está ChromaDB) |
| `tsvector` / `tsquery` | Búsqueda por palabras completas, muy eficiente | Requiere normalización por idioma, sin búsqueda por prefijo parcial |
| Elasticsearch | Búsqueda avanzada | Infra adicional, innecesario para MVP |

## Decisión

- **Docker Compose** como único entorno de desarrollo local con `make up/down/db-init/logs`.
- **UUID v4** (`gen_random_uuid()`) como PK en todas las tablas. PG 16 lo incluye sin `uuid-ossp`.
- **`VARCHAR + CHECK`** para columnas de tipo enum (`status`, `priority`, `type`). Evita migraciones destructivas al añadir valores.
- **GIN trigram** (`pg_trgm`) en `tasks.title` y `knowledge_chunks.content` para búsqueda por substring.
- **Índice único parcial** `WHERE status = 'active'` en `sprints` para garantizar como máximo un sprint activo por proyecto, sin afectar a sprints en otros estados.
- **Trigger `set_updated_at()`** en `tasks` y `projects` para mantener `updated_at` sin lógica en la capa de aplicación.

## Consecuencias

**Positivas:**
- `make up && make db-init` en un equipo nuevo: entorno listo en < 2 minutos.
- El DDL es la documentación viva del schema; el compose file documenta las dependencias de infraestructura.
- Los `CHECK` constraints aceptan nuevos valores de enum sin migraciones de tipo.
- El índice parcial de sprint activo elimina lógica de validación en la capa de aplicación.

**Negativas / deuda:**
- Los PKs UUID generan índices ~20 % más grandes. Aceptable hasta que la tabla `tasks` supere los 10M de registros (improbable en MVP).
- Cuando Railway entre en producción, el `docker-compose.yml` local dejará de ser la referencia — se necesitará separar `docker-compose.override.yml` para dev vs prod.
- `VARCHAR + CHECK` no ofrece type-safety en el motor: una inserción con valor inválido da error en runtime, no en compilación. La validación Pydantic en la capa de aplicación mitiga esto.

**Deuda técnica registrada:**
- DT-007: Crear `docker-compose.override.yml` cuando se active Railway para separar config local vs prod.
- DT-008: Evaluar migrar índices trigram a búsqueda vectorial completa vía ChromaDB cuando la base de documentos supere 5.000 chunks.
