# Definition of Done — PM Copilot

**Versión**: 0.1  
**Fecha**: 2026-04-24  

---

## Introducción

El DoD estándar de desarrollo ágil asume comportamientos deterministas: dado un input, el output es siempre el mismo. Los sistemas con LLMs rompen este supuesto: el mismo prompt puede generar outputs distintos en cada ejecución.

Este documento define criterios de done adaptados a ese contexto, diferenciando entre:
- **Features deterministas**: lógica de negocio clásica (CRUD, cálculos, integraciones)
- **Features LLM**: estimaciones, generación de texto, clasificaciones, respuestas RAG

---

## 1. Criterios Universales (toda historia)

### Código
- [ ] El código pasa el linter (`ruff` para Python, `ESLint` para TypeScript) sin warnings
- [ ] El código tiene type hints completos (Python) o tipos estrictos (TypeScript)
- [ ] No hay `print()` ni `console.log()` de debug — solo logging estructurado
- [ ] No hay credenciales, URLs de producción o datos personales hardcodeados
- [ ] Las dependencias nuevas están añadidas en `pyproject.toml` o `package.json`

### Tests
- [ ] Los tests unitarios pasan (`pytest` / `vitest`)
- [ ] No se ha reducido el coverage de dominio y aplicación por debajo del umbral (> 80%)
- [ ] Los tests nuevos tienen nombres descriptivos que explican el escenario

### Documentación
- [ ] La API nueva está documentada en OpenAPI (FastAPI lo genera automáticamente)
- [ ] Si la feature introduce un nuevo port o adaptador, está descrito en `ARCHITECTURE.md`
- [ ] Si se tomó una decisión arquitectónica relevante, hay un ADR nuevo o actualizado

### Integración
- [ ] El PR pasa CI (GitHub Actions): linting, tests, type checking
- [ ] No hay conflictos de merge pendientes
- [ ] La feature está detrás de un feature flag si es experimental (opcional en MVP)

---

## 2. Criterios para Features Deterministas

### Backend
- [ ] Tests unitarios para el caso de uso con mocks de todos los ports
- [ ] Tests de integración para los adaptadores nuevos (al menos contra mock del servicio externo)
- [ ] Los errores posibles están documentados y manejados (HTTP status codes correctos)
- [ ] Los endpoints nuevos están probados con `httpx.AsyncClient` en tests de integración

### Frontend
- [ ] El componente nuevo tiene al menos un test de renderizado (`vitest` + Testing Library)
- [ ] La feature funciona en Chrome, Firefox y Safari (última versión)
- [ ] La feature es responsive (mobile ≥ 375px, desktop ≥ 1024px)
- [ ] No hay regresiones visuales obvias en las páginas existentes

---

## 3. Criterios Especiales para Features LLM (No Deterministas)

### 3.1 Criterios de Aceptación LLM

Los criterios de aceptación de user stories LLM deben seguir este patrón:

```
DADO [contexto del proyecto conocido]
CUANDO [el usuario hace X]
ENTONCES el sistema produce un output que [criterio evaluable]:
  - Tiene el formato correcto (JSON schema, estructura esperada)
  - Contiene los campos requeridos (no vacíos, tipos correctos)
  - Cumple el criterio de calidad en ≥ 8 de 10 ejecuciones con prompts de prueba representativos
  - Si el output es inválido, hace fallback a [comportamiento alternativo definido]
```

**No válido como criterio de aceptación LLM**:
- ❌ "El LLM genera una estimación correcta"
- ❌ "La respuesta es relevante"
- ❌ "El chatbot entiende la pregunta"

**Válido como criterio de aceptación LLM**:
- ✅ "La estimación devuelta es un número entre 1 y 100 en formato JSON `{points: int, confidence: float}`"
- ✅ "En 8/10 ejecuciones con tareas del conjunto de prueba, la estimación está dentro del ±30% de la media del equipo"
- ✅ "Si el output no parsea como JSON válido, el sistema retorna un error 422 con mensaje descriptivo"
- ✅ "Los chunks RAG citados en la respuesta pertenecen a documentos del espacio PBPMIA"

### 3.2 Testing de Features LLM

- [ ] Existe un **conjunto de prueba canónico** con ≥ 5 inputs representativos para la feature
- [ ] El output se valida contra un **JSON schema** o estructura definida
- [ ] Los tests de LLM se ejecutan con `LLM_MODE=local` (Ollama) en CI para evitar costes
- [ ] Existe al menos 1 test que verifica el **comportamiento de fallback** si el LLM devuelve output inválido
- [ ] El **umbral de confianza** está definido y documentado en el criterio de aceptación

### 3.3 Evaluación de Calidad (E2E, no en CI)

Para features críticas (estimación, generación de informes), se ejecuta periódicamente:

- **Golden set evaluation**: ejecutar la feature sobre 10-20 casos reales conocidos y medir la tasa de aceptación manual
- **Regression check**: comparar con la versión anterior del prompt si el prompt cambia
- Los resultados se documentan en `docs/PROMPTS.md` en la sección del prompt correspondiente

### 3.4 Observabilidad LLM

- [ ] Cada llamada LLM loguea: `provider`, `task_type`, `input_tokens`, `output_tokens`, `latency_ms`, `fallback_used`
- [ ] Los errores de parsing del output LLM se loguean con el output completo (para debugging)
- [ ] Las métricas de uso por proveedor son visibles en el dashboard

---

## 4. Criterios para Integraciones Externas

- [ ] El adaptador tiene Circuit Breaker configurado (ver `ADR-003`)
- [ ] El adaptador tiene tests de integración con mock del servicio externo (usando `pytest-httpx` o similar)
- [ ] El comportamiento de fallback está implementado y testeado
- [ ] Los errores de autenticación (401, 403) se manejan con mensaje de error descriptivo al usuario

---

## 5. Criterios de Seguridad

- [ ] Ninguna credential aparece en logs o responses de API
- [ ] Los inputs del usuario son validados con Pydantic antes de usarse en prompts LLM (prevención de prompt injection)
- [ ] Los endpoints nuevos tienen autenticación si la feature requiere identidad del usuario
- [ ] Los datos de terceros (Jira, Confluence, GitHub) no se persisten más allá de lo necesario para la feature

---

## 6. Checklist de Release (Sprint Review)

Al cerrar un sprint, verificar adicionalmente:

- [ ] Las métricas de calidad LLM están dentro de los umbrales para las features del sprint
- [ ] La velocidad del sprint (puntos completados) está registrada en el sistema de tracking
- [ ] Los prompts nuevos creados durante el sprint están añadidos a `docs/PROMPTS.md`
- [ ] Las lecciones aprendidas del sprint están en la página Confluence "04. Lecciones Aprendidas"
- [ ] El backlog está priorizado para el próximo sprint
