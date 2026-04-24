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

*[Añadir prompts de desarrollo backend aquí]*

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

*[Añadir prompts de integraciones (Jira, Confluence, GitHub) aquí]*

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
