# ADR-002 — Arquitectura Hexagonal vs Microservicios

**Estado**: Aceptado  
**Fecha**: 2026-04-24  
**Autor**: Marcos Vese  

---

## Contexto

PM Copilot tiene múltiples integraciones externas (Confluence, Jira, GitHub, dos LLMs, ChromaDB, PostgreSQL) y lógica de negocio no trivial (estimación, RAG, generación de documentos). Necesitamos una arquitectura que:

1. Permita testear la lógica de negocio aislada de las integraciones
2. Facilite cambiar o añadir integraciones sin afectar el dominio
3. Sea mantenible por un equipo pequeño (inicialmente 1 desarrollador)
4. Prepare el camino para una posible migración a microservicios si el proyecto escala

Las opciones evaluadas son:
- **A) Arquitectura hexagonal (monolito modular)** — un solo proceso Python con dominio aislado
- **B) Microservicios desde el inicio** — servicios independientes por dominio (LLM service, RAG service, etc.)
- **C) Arquitectura en capas tradicional (MVC)** — más simple pero sin aislamiento del dominio

---

## Decisión

**Arquitectura hexagonal (Ports & Adapters)** con un monolito modular.

---

## Razonamiento

### Por qué no microservicios desde el inicio

Los microservicios aportan complejidad operacional inmediata que no está justificada en esta fase:

- **Overhead de infraestructura**: service discovery, malla de servicios, orquestación (K8s), comunicación entre servicios (gRPC, message brokers), observabilidad distribuida
- **Latencia de red**: cada llamada entre servicios añade latencia; en un flujo RAG esto se multiplicaría (query → embedding service → vector store → LLM service → response)
- **Consistencia transaccional**: garantizar consistencia entre múltiples servicios independientes requiere patrones complejos (sagas, eventos)
- **Coste de desarrollo**: en un equipo de 1, el overhead de mantener múltiples repositorios, pipelines CI/CD y despliegues independientes ralentizaría el desarrollo en un factor 3-5x

> El patrón de microservicios es la solución al problema de **escalar equipos**, no código. Con un equipo de 1-3 personas, los microservicios son prematuros.

### Por qué hexagonal y no MVC en capas

La arquitectura en capas tradicional (controllers → services → repositories) permite que la lógica de negocio filtre hacia las capas de infraestructura con el tiempo (el "Big Ball of Mud" progressivo). En un sistema con múltiples LLMs, RAG y APIs externas, este riesgo es especialmente alto.

La arquitectura hexagonal añade:
- **Inversión de dependencias**: el dominio define interfaces (ports), la infraestructura las implementa. El dominio nunca depende de Jira, Claude o PostgreSQL directamente
- **Testabilidad**: los casos de uso se testean con mocks de los ports sin necesidad de servicios externos
- **Intercambiabilidad**: sustituir ChromaDB por Qdrant, o Claude por GPT-4, es un cambio en el adaptador secundario, no en el dominio
- **Preparación para microservicios**: cuando sea el momento de extraer un servicio (p.ej. el RAG engine), los límites del módulo ya están definidos

### Cómo preparamos la migración a microservicios

La arquitectura hexagonal actual establece **bounded contexts claros** que coinciden con los potenciales microservicios futuros:

```
Monolito Hexagonal Actual          →    Microservicios Futuros (si aplica)
─────────────────────────────────────────────────────────────────────────
domain/entities/task.*                   Task Management Service
domain/entities/estimation.*             Estimation Service
infrastructure/rag/                      RAG Service
infrastructure/llm_router/               LLM Gateway Service
adapters/secondary/jira.*                Jira Integration Service
adapters/secondary/confluence.*          Confluence Integration Service
```

Cuando sea el momento de extraer un servicio:
1. El módulo ya está aislado con interfaces claras (ports)
2. Se reemplaza el adaptador local por un adaptador HTTP/gRPC
3. El caso de uso no cambia

---

## Reglas de Implementación

Para mantener la integridad hexagonal:

1. **El módulo `domain/` no tiene dependencias externas** — solo Python estándar. `import jira`, `import anthropic`, `import sqlalchemy` nunca aparecen en `domain/`.

2. **Las dependencias fluyen hacia adentro**: `adapters → application → domain`. Nunca en sentido contrario.

3. **Los ports son abstractos**: usar `abc.ABC` y `@abstractmethod` para definir ports. Los casos de uso reciben ports por inyección de dependencias.

4. **Los adaptadores son intercambiables**: si hoy `VectorStorePort` es implementado por `ChromaDBAdapter`, mañana puede ser `QdrantAdapter` sin tocar los casos de uso.

---

## Consecuencias

### Positivas
- Lógica de negocio testeable sin servicios externos (unit tests rápidos y fiables)
- Integraciones intercambiables — facilita evolución del stack
- Boundary contexts bien definidos para migración futura
- Complejidad operacional mínima: un solo proceso, un solo despliegue
- Código estructurado que comunica las intenciones del dominio claramente

### Negativas / Trade-offs
- Más estructura inicial que MVC: requiere definir ports, adaptadores y use cases explícitamente
- Mayor curva de aprendizaje para contribuidores nuevos
- No escala horizontalmente por dominio (si el LLM service necesita más recursos que el resto, no puede escalarse independientemente en esta fase)

### Deuda Técnica Registrada

**DT-001: Evaluación de migración a microservicios**  
Trigger: cuando el equipo supere 3 personas O cuando los recursos de cómputo del LLM engine justifiquen escalado independiente.  
Acción: extraer RAG engine y LLM Router como servicios separados usando los boundary contexts definidos.  
Estimación: 3-4 semanas de trabajo cuando llegue el momento.
