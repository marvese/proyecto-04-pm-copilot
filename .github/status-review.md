# Status Review

**Version**: 0.1  
**Last Updated**: 2026-05-05  
**Owner**: Marcos Vese

**Skill asociado**: `/.github/skill-status-review.md`

<!--
Este documento sirve como registro vivo del estado del código.

Uso recomendado:
1. Añade una nueva entrada en "Revisión Actual" o mueve la actual al historial.
2. Mantén los hallazgos priorizados por severidad e impacto.
3. Referencia siempre archivos, módulos o decisiones concretas.
4. Actualiza la tabla de historial al final de cada revisión.
-->

## Objetivo

Llevar un seguimiento periódico del estado real del código, detectar desviaciones entre documentación e implementación, y dejar trazabilidad de riesgos, decisiones y acciones recomendadas.

## Cómo usar este documento

<!--
Mantén esta sección estable. Las revisiones nuevas deberían afectar sobre todo:
- Revisión actual
- Hallazgos
- Riesgos
- Acciones recomendadas
- Historial de revisiones
-->

- Registrar una revisión por fecha relevante.
- Resumir el estado por áreas, no solo por archivos.
- Diferenciar entre fortalezas, brechas y riesgos.
- Priorizar las acciones para facilitar planificación en Jira o backlog.

## Revisión Actual

**Fecha**: 2026-05-05  
**Tipo**: Revisión de seguimiento arquitectónico y de implementación  
**Alcance**: Documentación, backend, frontend, testing y operativa  
**Nota**: se ignora explícitamente `/.github/status-review-claude.md` en esta revisión.

### Resumen Ejecutivo

El proyecto mantiene una base fuerte en arquitectura, documentación y estructura backend. El mayor cambio desde la revisión anterior es que el frontend ha dejado de ser principalmente stub y ahora tiene más superficie funcional real, incluyendo PWA, navegación, dashboard, tareas e informes. El problema central ya no es solo la ausencia de frontend, sino una deriva de contrato entre frontend y backend: la UI ya consume endpoints y flujos que el backend aún no implementa. El MVP sigue bloqueado por autenticación ausente, CRUD de tareas/proyectos/reportes sin cerrar, persistencia de chat en memoria y ausencia de CI/CD visible.

### Estado por Áreas

| Área | Estado | Comentario |
|---|---|---|
| Documentación | Fuerte | PRD, ADRs, arquitectura y DoD están bien definidos |
| Arquitectura backend | Fuerte | Separación hexagonal consistente y DI clara |
| Backend funcional | Parcial | Estimación, RAG e integraciones externas avanzadas; tareas, proyectos, auth y reportes siguen incompletos |
| Frontend | En progreso | Ya no es un stub generalizado; creció más rápido que el backend y ahora depende de endpoints no implementados |
| Seguridad | Crítico | Autenticación declarada pero no implementada |
| Testing | Medio | Buenas pruebas en backend; siguen faltando pruebas frontend y E2E relevantes |
| CI/CD y operación | Débil | No hay pipeline visible y `make test` no existe en el Makefile actual |

### Fortalezas Confirmadas

<!--
Mantén aquí solo fortalezas ya verificadas en código o pruebas.
Evita incluir intenciones o backlog futuro.
-->

1. La arquitectura hexagonal está bien planteada y respetada en la estructura del backend.
2. El flujo de estimación está implementado y expuesto en API.
3. La persistencia PostgreSQL ya dispone de pruebas de integración útiles.
4. El stack documental del proyecto está por encima de la media para esta fase.
5. Los adaptadores de Jira, Confluence y GitHub ya cuentan con implementación funcional y retries.
6. El frontend avanzó de forma tangible: `projectService`, `taskService`, `reportService`, `useProjectContext`, `useTasks`, `DashboardPage`, `TasksPage`, `ReportsPage` y la PWA ya tienen implementación real.

### Hallazgos Prioritarios

<!--
Formato recomendado para futuras revisiones:
- Severidad: Crítica / Alta / Media / Baja
- Hallazgo
- Evidencia
- Impacto
-->

1. **[Pendiente] Crítica**: La autenticación existe en especificación y routing, pero no en implementación efectiva.  
   Evidencia: `backend/src/adapters/primary/api/auth_router.py` sigue lanzando `NotImplementedError`.

2. **[Pendiente] Alta**: Los endpoints de tareas siguen publicados pero todavía lanzan `NotImplementedError`.  
   Evidencia: `backend/src/adapters/primary/api/tasks_router.py`.

3. **[Pendiente] Alta**: Los endpoints de reportes siguen definidos, pero el caso de uso y la API continúan pendientes.  
   Evidencia: `backend/src/adapters/primary/api/reports_router.py`, `backend/src/application/use_cases/generate_report_use_case.py`.

4. **[Pendiente] Alta**: La persistencia del chat no cumple todavía la especificación funcional; sigue en memoria.  
   Evidencia: `backend/src/adapters/primary/api/chat_router.py`, `docs/FUNCTIONAL_SPEC.md`.

5. **[Parcialmente resuelto / reformulado] Alta**: El frontend ya no está mayoritariamente en modo stub, pero ahora aparece una incoherencia más grave: consume endpoints y capacidades backend que no existen o siguen sin implementación.  
   Evidencia: `frontend/src/services/projectService.ts`, `frontend/src/services/taskService.ts`, `frontend/src/services/reportService.ts` frente a `backend/src/adapters/primary/api/projects_router.py`, `backend/src/adapters/primary/api/tasks_router.py`, `backend/src/adapters/primary/api/reports_router.py`.

6. **[Parcialmente resuelto] Media**: La resiliencia frente a fallos externos mejoró en Jira, Confluence y GitHub, pero sigue siendo parcial en otros caminos críticos.  
   Evidencia: `backend/src/adapters/secondary/integrations/jira_adapter.py`, `backend/src/adapters/secondary/integrations/confluence_adapter.py`, `backend/src/adapters/secondary/integrations/github_adapter.py`; persiste brecha en `backend/src/infrastructure/llm_router/llm_router.py` para streaming.

7. **[En curso / casi resuelto] Baja**: La promesa PWA ya no está en estado mínimo; ahora hay manifest completo, iconos, `vite-plugin-pwa` y `runtimeCaching`.  
   Evidencia: `frontend/vite.config.ts`, `frontend/public/manifest.json`.

8. **[Nuevo] Alta**: El frontend consume `GET /api/v1/projects/{id}/status`, pero el backend no expone ese endpoint aunque sí existe el caso de uso de agregación.  
   Evidencia: `frontend/src/services/projectService.ts`, `backend/src/adapters/primary/api/projects_router.py`, `backend/src/application/use_cases/query_project_status_use_case.py`.

9. **[Nuevo] Alta**: El contenedor DI no ha evolucionado al ritmo del frontend ni del changelog; sigue sin cablear casos de uso y adaptadores necesarios para tareas, estado de proyecto y reportes.  
   Evidencia: `backend/src/infrastructure/container.py`.

10. **[Nuevo] Media**: `estimationService` del frontend sigue sin implementación pese a que el backend de estimación está operativo desde hace tiempo.  
    Evidencia: `frontend/src/services/estimationService.ts`, `backend/src/adapters/primary/api/estimate_router.py`.

11. **[Nuevo] Media**: El crecimiento del frontend no está acompañado por pruebas automáticas visibles en esa capa.  
    Evidencia: no se localizaron ficheros de test en `frontend/src/`.

12. **[Nuevo] Media**: La preparación operativa sigue débil; no hay workflows en `/.github/workflows` y `make test` falla porque ese target no existe en `Makefile`.  
    Evidencia: `Makefile`, ausencia de `/.github/workflows/`.

### Riesgos Activos

<!--
Describe riesgos que afecten seguridad, entrega, operación o calidad.
Si un riesgo queda mitigado, elimínalo o muévelo a una revisión histórica.
-->

- Riesgo de seguridad por ausencia de autenticación y autorización reales.
- Riesgo de delivery por gap entre documentación avanzada, frontend ya desarrollado y backend todavía incompleto.
- Riesgo de integración por deriva de contrato entre frontend y backend.
- Riesgo de regresión en frontend por ausencia de pruebas funcionales significativas.
- Riesgo operativo por falta de pipeline CI/CD y observabilidad mínima para release.

### Acciones Recomendadas

<!--
Prioriza aquí acciones concretas y ejecutables.
Si más adelante se enlazan con Jira, añade el identificador de issue.
-->

1. Cerrar el contrato backend que hoy bloquea al frontend: implementar `projects`, `projects/{id}/status`, CRUD de tareas y endpoints de reportes.
2. Implementar autenticación JWT y protección de rutas sensibles.
3. Completar `CreateTaskUseCase`, `UpdateTaskUseCase`, `GenerateReportUseCase` y cableado en `container.py`.
4. Implementar `estimationService` en frontend para alinear la UI con el backend de estimación ya existente.
5. Migrar la persistencia del chat a PostgreSQL para alinear código y especificación.
6. Completar la resiliencia pendiente en `LLMRouter.stream()` y revisar retries de otros adaptadores críticos.
7. Añadir pipeline mínima de CI con lint, tests unitarios e integración crítica, y definir un target de test consistente en `Makefile`.
8. Introducir pruebas frontend básicas para `useProjectContext`, `useTasks` y las páginas principales.

### Plan de Acción Propuesto

#### Fase P0 — Desbloqueo del MVP

1. Implementar `GET /api/v1/projects`, `POST /api/v1/projects`, `GET /api/v1/projects/{id}` y `GET /api/v1/projects/{id}/status`.
2. Implementar `GET/POST/PATCH/DELETE` de tareas y `POST /tasks/{id}/sync-jira`.
3. Implementar autenticación mínima JWT o, si se difiere, marcar explícitamente la app como single-user dev-only.

#### Fase P1 — Coherencia funcional entre capas

1. Completar generación de reportes en backend y reutilizar el endpoint de descarga ya definido.
2. Completar `estimationService` y `useEstimation` en frontend.
3. Conectar el contenedor DI con todos los casos de uso realmente consumidos por routers y frontend.

#### Fase P2 — Calidad y operación

1. Añadir tests frontend de hooks y smoke tests de páginas.
2. Crear `/.github/workflows` con lint, typecheck y tests mínimos.
3. Revisar `Makefile` para exponer `make test`, `make test-backend` y `make test-frontend`.

## Historial de Revisiones

<!--
Añade nuevas filas y conserva trazabilidad cronológica.
Si la revisión actual cambia de forma importante, resume el cambio aquí antes de reemplazarla.
-->

| Fecha | Versión | Tipo | Resumen |
|---|---|---|---|
| 2026-05-05 | 0.1 | Revisión de seguimiento | El frontend avanzó de forma sustancial, pero emergió un desacoplo fuerte con el backend; se marcaron hallazgos resueltos, en curso y nuevos riesgos de integración |
| 2026-05-04 | 0.1 | Revisión inicial | Primera revisión formal del estado del código, arquitectura y madurez del MVP |