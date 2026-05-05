# Status Review — Claude

**Version**: 0.2  
**Last Updated**: 2026-05-05  
**Owner**: Claude (generado automáticamente)

<!--
Este fichero es generado por Claude al final de cada sesión de revisión.
El fichero canónico para revisión personal es status-review.md.
-->

## Revisión Actual

**Fecha**: 2026-05-05  
**Tipo**: Revisión de progreso — cierre épica PMCP-37 (Frontend)  
**Alcance**: Frontend completo, backend funcional, estado de hallazgos previos

### Resumen Ejecutivo

El proyecto da un salto significativo en madurez de producto: la épica PMCP-37 cierra el gap crítico del frontend, conectando la SPA React con el backend real (proyectos, tareas, reportes). El stack visible al usuario está ahora en estado alfa funcional. Las brechas críticas que quedan son autenticación, los endpoints de tareas/reportes en backend (aún `NotImplementedError`) y la ausencia de CI/CD.

### Estado por Áreas

| Área | Estado | Cambio vs 2026-05-04 | Comentario |
|---|---|---|---|
| Documentación | Fuerte | = | CHANGELOG, ARCHITECTURE, INSTALL y RUNBOOK actualizados |
| Arquitectura backend | Fuerte | = | Hexagonal consistente, DI clara |
| Backend funcional | Parcial | = | Estimación y RAG operativos; tasks/reports/auth pendientes |
| Frontend | Funcional | ↑ **Mejorado** | SPA completa — dashboard, tasks, reports, chat; servicios conectados; PWA con Workbox |
| Seguridad | Crítico | = | Auth router existe pero no implementa JWT real |
| Testing | Medio | = | 175 tests backend pasando; sin tests de componentes React |
| CI/CD y operación | Débil | = | Sin pipeline CI visible |

### Fortalezas Confirmadas

1. La arquitectura hexagonal está bien planteada y respetada en la estructura del backend.
2. El flujo de estimación está implementado y expuesto en API.
3. La persistencia PostgreSQL ya dispone de pruebas de integración útiles (18 tests).
4. El stack documental del proyecto está por encima de la media para esta fase.
5. **Nuevo**: Frontend SPA completo y funcional — routing, estado, servicios API, PWA production-ready.
6. **Nuevo**: TypeScript sin errores (`tsc --noEmit` limpio) en toda la capa frontend.

### Hallazgos Prioritarios

1. **Crítica**: La autenticación existe en especificación y routing, pero no en implementación efectiva.
   Evidencia: `backend/src/adapters/primary/api/auth_router.py`.

2. **Alta**: Los endpoints de tareas están publicados pero todavía lanzan `NotImplementedError`.
   Evidencia: `backend/src/adapters/primary/api/tasks_router.py`.

3. **Alta**: Los endpoints de reportes están definidos, pero el caso de uso y la API siguen pendientes.
   Evidencia: `backend/src/adapters/primary/api/reports_router.py`, `backend/src/application/use_cases/generate_report_use_case.py`.

4. **Alta**: La persistencia del chat sigue en memoria; no cumple la especificación funcional.
   Evidencia: `backend/src/adapters/primary/api/chat_router.py`, `docs/FUNCTIONAL_SPEC.md`.

5. **Media** ~~(antes Alta)~~: El frontend conecta todos los módulos core; queda pendiente la UI de estimación.
   Evidencia: `frontend/src/hooks/useEstimation.ts` (stub), `frontend/src/services/estimationService.ts` (stub).

6. **Media**: Resiliencia parcial; no todos los caminos aplican circuit breaker/retry consistentemente.
   Evidencia: `backend/src/infrastructure/llm_router/llm_router.py`, adaptadores externos.

7. ~~**Media**: La promesa PWA está en estado mínimo~~ — **Resuelto**: `vite-plugin-pwa` + Workbox implementado con estrategia `NetworkFirst` para `/api/*`.

### Riesgos Activos

- Riesgo de seguridad por ausencia de autenticación y autorización reales.
- Riesgo de delivery: backend tasks/reports sin implementar bloquean el flujo end-to-end en producción.
- Riesgo de regresión en frontend por ausencia de pruebas de componentes React.
- Riesgo operativo por falta de pipeline CI/CD y observabilidad mínima para release.

### Acciones Recomendadas (prioridad actualizada)

1. **P0** — Implementar `CreateTaskUseCase` y `UpdateTaskUseCase` en backend + wiring DI (desbloquea el CRUD end-to-end con el frontend nuevo).
2. **P0** — Implementar autenticación JWT y protección de rutas sensibles.
3. **P1** — Implementar `GenerateReportUseCase` + endpoints de reportes.
4. **P1** — Migrar la persistencia del chat a PostgreSQL (alinear código y especificación).
5. **P2** — Añadir pipeline mínima de CI (lint, typecheck, pytest -m "not integration").
6. **P2** — Conectar UI de estimación al hook `useEstimation` y servicio real.

## Historial de Revisiones

| Fecha | Versión | Tipo | Resumen |
|---|---|---|---|
| 2026-05-05 | 0.2 | Revisión de progreso | Cierre épica PMCP-37: frontend SPA completo. Actualización de hallazgos y prioridades |
| 2026-05-04 | 0.1 | Revisión inicial | Primera revisión formal del estado del código, arquitectura y madurez del MVP |
