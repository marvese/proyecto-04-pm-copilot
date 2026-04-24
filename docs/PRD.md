# PRD — PM Copilot

**Versión**: 0.1  
**Estado**: Draft  
**Fecha**: 2026-04-24  
**Autor**: Marcos Vese  

---

## 1. Resumen Ejecutivo

PM Copilot es un asistente inteligente para gestión de proyectos de software que combina RAG (Retrieval-Augmented Generation) con integraciones nativas a Confluence, Jira y GitHub. Permite a PMs y tech leads obtener estimaciones, crear tareas, generar informes y mantener el estado del proyecto consultando en lenguaje natural, con conocimiento contextual del proyecto propio.

El sistema sirve además como demostración y laboratorio de la metodología **PM con IA**: un marco de desarrollo ágil adaptado a la colaboración humano-LLM donde cada decisión, prompt y aprendizaje queda documentado y reutilizable.

---

## 2. Problema

Los PMs de proyectos de software pasan entre el 40-60% de su tiempo en tareas repetitivas de documentación, seguimiento y coordinación: actualizar Jira, redactar informes de estado, estimar historias, crear actas de reunión, consolidar información dispersa en Confluence y GitHub. Estas tareas consumen tiempo que debería dedicarse a desbloqueadores, priorización y comunicación con stakeholders.

Los LLMs genéricos (ChatGPT, Claude.ai) pueden ayudar, pero no tienen contexto del proyecto específico: no conocen las historias pasadas, la velocidad del equipo, las convenciones de naming, el historial de decisiones ni los documentos internos.

---

## 3. Visión del Producto

> Un PM copilot que conoce tu proyecto tan bien como tú, disponible 24/7, que ejecuta en tu nombre las tareas repetitivas y amplifica tu capacidad de toma de decisiones con contexto enriquecido.

---

## 4. Usuarios Objetivo

### Persona Principal: PM Técnico
- Gestiona 1-3 proyectos de software simultáneamente
- Familiarizado con Jira, Confluence y GitHub
- Cómodo con herramientas de IA en su flujo de trabajo
- Necesita visibilidad rápida del estado del proyecto

### Persona Secundaria: Tech Lead
- Responsable de estimaciones técnicas y arquitectura
- Participa en planning y revisiones
- Necesita generar documentación técnica rápidamente

### Persona Terciaria: Equipo de Desarrollo
- Consume tareas creadas por el sistema
- Puede consultar al copilot sobre contexto del proyecto
- Actualiza estado de tareas (integrado en Jira)

---

## 5. Capacidades Principales (Prioridad MoSCoW)

### Must Have — MVP

**M1. Estimación y Planificación**
- Estimar historias de usuario en puntos/días basándose en el historial del proyecto
- Descomponer epics en historias y tareas con estimaciones
- Identificar dependencias y riesgos en el backlog
- Contexto RAG: velocidad histórica, complejidad de features similares, equipo

**M2. Creación y Gestión de Tareas**
- Crear tareas en el gestor propio (PostgreSQL) con estructura definida
- Sincronizar con Jira (crear issues, actualizar estado, asignar)
- Actualizar tareas por lenguaje natural: "cierra la tarea 42 y añade la nota X"

**M3. Generación de Informes y Documentos**
- Informe de estado del sprint (MD y DOCX)
- Acta de reunión estructurada desde notas o transcripción
- Generación de documentación técnica (README, ADRs)
- Exportación a XLSX para reportes ejecutivos

**M4. Seguimiento y Estado del Proyecto**
- Dashboard de estado actual: sprint activo, velocidad, riesgos
- Consultas en lenguaje natural: "¿qué bloqueadores hay esta semana?"
- Alertas automáticas por desviaciones de plan

### Should Have — v1.1

**S1. RAG sobre documentación del proyecto**
- Indexación automática de páginas Confluence del proyecto
- Indexación de PRs y issues de GitHub
- Respuestas contextuales: "¿cómo manejamos X según nuestros docs?"

**S2. Integración GitHub profunda**
- Crear PRs desde descripción de tarea
- Resumen automático de PRs para revisión
- Correlación commit → tarea

**S3. Modo offline básico (PWA)**
- Acceso a última sincronización de estado sin conexión
- Encolado de comandos para sincronizar al reconectar

### Could Have — v2.0

**C1. Análisis predictivo**
- Predicción de fecha de entrega basada en velocidad real
- Detección temprana de scope creep
- Sugerencias de replanificación

**C2. Retrospectiva asistida**
- Análisis automático del sprint: qué fue bien, qué falló
- Comparación con sprints anteriores

### Won't Have — Fuera de Scope MVP

- Gestión de presupuestos o recursos financieros
- Integración con herramientas de RRHH
- Funcionalidades de chat grupal en tiempo real
- App móvil nativa (planificada como POC Flutter post-MVP)

---

## 6. Requisitos No Funcionales

| Requisito | Objetivo |
|-----------|----------|
| Latencia P95 API | < 2s para queries simples, < 8s para generación de documentos |
| Latencia conversacional | < 500ms primer token (streaming) |
| Disponibilidad backend | 99.5% uptime (Railway SLA) |
| Precisión de estimaciones | ±20% vs estimación manual en retrospectiva |
| Relevancia RAG | Top-3 chunks relevantes en > 80% de queries de prueba |
| Fallback LLM | Degradación graciosa si Claude no disponible → Ollama |
| Seguridad | Credenciales solo en `.env`, nunca en código o logs |

---

## 7. Métricas de Éxito

### Métricas de Producto (3 meses post-lanzamiento)
- **Adopción**: ≥ 5 sesiones/semana de uso activo
- **Reducción de tiempo**: -30% tiempo en tareas de seguimiento y documentación
- **Precisión de estimaciones**: Error medio < 25% vs estimación manual
- **Satisfacción**: NPS interno ≥ 7/10

### Métricas Técnicas
- **Cache hit rate RAG**: > 60% de queries resueltas con contexto recuperado relevante
- **LLM Router**: > 40% de queries resueltas por Ollama (reducción de coste)
- **Circuit Breaker**: 0 fallos en cascada por dependencia externa
- **Coverage de tests**: > 80% en capa de dominio y aplicación

---

## 8. Constraints y Supuestos

### Constraints
- Desarrollo en solitario (1 developer) con apoyo de IA
- Presupuesto de API Anthropic: ~$20/mes en desarrollo
- Infraestructura limitada al tier gratuito/básico de Railway y Vercel
- Ollama disponible localmente (Mac/Linux con 16GB RAM mínimo)

### Supuestos
- El usuario tiene acceso a Confluence, Jira y GitHub con permisos de lectura/escritura
- El espacio Confluence `PBPMIA` es el repositorio de documentación principal
- Los modelos Ollama (`llama3`, `nomic-embed-text`) están instalados localmente
- La latencia de Claude API es aceptable para el caso de uso conversacional

---

## 9. Roadmap de Alto Nivel

| Fase | Duración | Entregables |
|------|----------|-------------|
| **Fase 0: Fundación** | 2 semanas | Infraestructura hexagonal, LLM Router, RAG básico |
| **Fase 1: MVP Core** | 3 semanas | M1 + M2 + M3 básico, Frontend chat |
| **Fase 2: Integraciones** | 2 semanas | Jira + GitHub adapters, M4 dashboard |
| **Fase 3: RAG Enriquecido** | 2 semanas | S1: indexación Confluence + GitHub |
| **Fase 4: Refinamiento** | 2 semanas | S2, optimización, métricas |
| **POC Flutter** | TBD | App móvil nativa (deuda técnica) |

---

## 10. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Latencia LLM inaceptable | Media | Alto | Streaming + indicadores de progreso |
| Hallucinations del LLM | Alta | Medio | RAG con fuentes citadas, validación de output |
| Límites de rate API Anthropic | Baja | Alto | Circuit Breaker + fallback a Ollama |
| Calidad de embeddings insuficiente | Media | Alto | Benchmark nomic-embed-text vs alternativas |
| Scope creep | Alta | Medio | 1-week sprints, backlog priorizado |
