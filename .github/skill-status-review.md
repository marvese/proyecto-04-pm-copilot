# Skill: status-review

## Objetivo

Realizar revisiones integrales del estado del proyecto (codigo, documentacion, coherencia funcional y operativa) y generar un informe accionable en `/.github/status-review-[timestamp].md`, con fecha y hora de ejecución de la revisión para mantener un histórico y poder comparar.

Este skill se usa cuando se necesite un reporte como el de arquitectura/estado general, no solo code review de un modulo aislado.

---

## Cuando activar este skill

Activar en cualquiera de estos casos:

- El usuario pida una revision de estado del proyecto.
- Se vaya a preparar una decision de roadmap o release.
- Se detecte brecha entre lo documentado y lo implementado.
- Se cierre un bloque importante de trabajo y se quiera recalibrar prioridades.

---

## Entradas minimas

Antes de ejecutar la revision, confirmar estas entradas:

1. Alcance temporal: revision puntual o desde la ultima revision registrada.
2. Alcance tecnico: backend, frontend, docs, infra, tests, CI/CD.
3. Objetivo: diagnostico ejecutivo, plan tecnico, o ambos.

Si el usuario no da estos datos, usar por defecto:

- Alcance temporal: desde la ultima fila del historial en `/.github/status-review.md`.
- Alcance tecnico: todo el repositorio.
- Objetivo: resumen ejecutivo + plan de accion priorizado.

---

## Fuentes obligatorias a revisar

Revisar siempre, como minimo:

- `docs/PRD.md`
- `docs/FUNCTIONAL_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/DEFINITION_OF_DONE.md`
- `CHANGELOG.md`
- `backend/src/` (use cases, routers, adapters, DI)
- `frontend/src/` (pages, hooks, services)
- `backend/tests/` y `frontend` tests si existen

Opcional segun contexto:

- `docs/INSTALL.md`, `docs/RUNBOOK.md`
- `.github/` (workflows, templates)
- scripts operacionales en `scripts/`

---

## Flujo de revision (paso a paso)

1. **Levantar baseline de contexto**
   - Leer documentacion de producto/arquitectura y estado declarado en changelog.
   - Identificar que promete el sistema vs que esta realmente implementado.

2. **Auditar implementacion real**
   - Backend: endpoints, casos de uso, adaptadores, integraciones, seguridad.
   - Frontend: rutas, servicios API, hooks, estados de carga/error, UX basica.
   - Pruebas: cobertura por capas, huecos en unit/integration/e2e.

3. **Detectar incoherencias y riesgos**
   - Documentacion vs codigo.
   - ADRs vs implementacion.
   - DoD vs estado de calidad actual.
   - Riesgos de seguridad, operacion, entrega y mantenibilidad.

4. **Clasificar hallazgos por severidad**
   - Critica: bloquea release o compromete seguridad/integridad.
   - Alta: afecta fuertemente funcionalidades core o plazos.
   - Media: deuda tecnica importante, no bloqueante inmediata.
   - Baja: mejoras o refinamientos.

5. **Construir plan de accion**
   - Ordenar acciones por impacto, esfuerzo y dependencias.
   - Separar quick wins de trabajo estructural.
   - Proponer fases (P0/P1/P2 o Sprint 1/2/3).

6. **Actualizar informe en `/.github/status-review.md`**
   - Refrescar "Revision Actual".
   - Mover resumen anterior al historial si aplica.
   - Mantener trazabilidad de fecha, version y tipo de revision.

---

## Checklist de evaluacion

### A. Coherencia documental

- [ ] PRD, Functional Spec y Architecture no se contradicen entre si.
- [ ] El changelog refleja el estado real de implementacion.
- [ ] El DoD es aplicable al estado actual (sin checks imposibles o ausentes).

### B. Estado backend

- [ ] Endpoints core implementados (sin `NotImplementedError` en rutas activas).
- [ ] Casos de uso principales implementados y cableados en DI.
- [ ] Integraciones externas con estrategia de resiliencia.
- [ ] Seguridad basica (authn/authz) implementada donde corresponde.

### C. Estado frontend

- [ ] Servicios API realmente conectados al backend.
- [ ] Hooks principales implementados (sin stubs bloqueantes).
- [ ] Paginas core funcionales para el objetivo de release.
- [ ] Manejo de estados de carga y error visible para el usuario.

### D. Calidad y testabilidad

- [ ] Existe cobertura minima en logica critica backend.
- [ ] Existen pruebas de integracion para adaptadores clave.
- [ ] Se identifican huecos de e2e en flujos prioritarios.

### E. Operacion y release readiness

- [ ] Flujo de CI/CD definido o gap explicitado.
- [ ] Runbook/Install alineados con lo que realmente funciona.
- [ ] Riesgos operativos y de despliegue documentados.

---

## Formato de salida requerido

La salida de la revision debe incluir, en este orden:

1. Hallazgos (ordenados por severidad, con evidencia).
2. Preguntas abiertas o supuestos.
3. Resumen ejecutivo (corto).
4. Plan de accion priorizado (con fases o prioridades).

Formato recomendado por hallazgo:

```
[SEVERIDAD] area
Problema: ...
Evidencia: ruta(s) de archivo
Impacto: ...
Accion sugerida: ...
```

---

## Plantilla rapida para ejecutar este skill

Usar este prompt de arranque:

"Ejecuta el skill status-review sobre este repositorio con alcance completo. Revisa documentacion e implementacion real, detecta incoherencias y riesgos, y actualiza `/.github/status-review.md` con fecha actual, hallazgos priorizados, resumen ejecutivo y plan de accion."

---

## Criterio de terminado

La ejecucion del skill se considera terminada cuando:

- Existe una "Revision Actual" actualizada en `/.github/status-review.md`.
- Los hallazgos tienen severidad y evidencia concreta.
- Hay plan priorizado y accionable.
- Se actualiza el historial de revisiones con una nueva fila.
