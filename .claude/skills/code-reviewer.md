# Skill: code-reviewer

## Cuándo se activa

Antes de cerrar cualquier feature: cuando el código de un módulo o adaptador esté completo y listo para considerarse terminado según `docs/DEFINITION_OF_DONE.md`. También se activa si el usuario pide explícitamente una revisión.

## Lista de verificación

Recorrer esta lista en orden. Reportar cada problema encontrado con: fichero, línea aproximada, descripción del problema y corrección sugerida. Si no hay problemas en una categoría, indicarlo brevemente.

---

### 1. Seguridad — bloqueante

Ningún problema en esta categoría puede quedar sin resolver.

- [ ] **Sin API keys hardcodeadas**: buscar patrones `sk-`, `Bearer `, cadenas de 40+ caracteres que parezcan tokens. Toda credencial llega de `os.environ` o de la configuración inyectada.
- [ ] **Sin secrets en logs**: las llamadas a `logger.*` no loguean objetos que puedan contener `api_key`, `token`, `password`, ni el contenido completo de prompts o respuestas LLM.
- [ ] **Sin ejecución de código generado**: si algún componente recibe código del LLM y lo ejecuta con `exec()` o `eval()`, señalarlo como bloqueante. No está permitido sin sandboxing explícito.
- [ ] **Inputs de usuario saneados** antes de usarlos en prompts LLM (prevención de prompt injection), queries de búsqueda o nombres de fichero.

---

### 2. Integridad de la arquitectura hexagonal — bloqueante

- [ ] **El dominio no importa infraestructura**: ningún fichero en `domain/` importa de `adapters/`, `infrastructure/`, `anthropic`, `groq`, `google.generativeai`, `httpx`, `sqlalchemy`, `chromadb`. Solo Python estándar y otras entidades de dominio.
- [ ] **El dominio no importa la aplicación**: ningún fichero en `domain/` importa de `application/`.
- [ ] **Los casos de uso trabajan con puertos**: en `application/use_cases/`, los atributos de dependencia son tipos `Port` (ABCs), nunca clases concretas de adaptadores.
- [ ] **Los adaptadores implementan puertos**: cada adaptador secundario hereda del puerto correspondiente y sobrescribe todos sus métodos abstractos.
- [ ] **Los adaptadores primarios no contienen lógica de negocio**: los FastAPI routers solo validan inputs (Pydantic), llaman a un use case, y formatean la respuesta. No hay `if/else` de negocio en los routers.

---

### 3. Circuit Breaker en integraciones externas — bloqueante

Toda llamada a un servicio externo debe estar protegida. Verificar los adaptadores secundarios:

- [ ] **Jira, Confluence, GitHub adapters**: cada método que llama a la API externa pasa por el Circuit Breaker configurado para ese servicio.
- [ ] **LLM adapters** (Anthropic, Groq, Gemini, Ollama): cada llamada pasa por Circuit Breaker con los parámetros definidos en `docs/ADR-003-circuit-breaker.md`.
- [ ] **ChromaDB adapter**: las operaciones de búsqueda e indexación tienen Circuit Breaker.
- [ ] **Comportamiento de fallback implementado**: cuando el Circuit Breaker está OPEN, el adaptador lanza una excepción tipada del dominio (no `CircuitOpenError` cruda) o ejecuta el fallback definido en el LLM Router.
- [ ] **No hay `except Exception: pass` silenciosos** en adaptadores — todo error debe loguearse o propagarse.

---

### 4. Uso correcto del LLM Router — bloqueante

- [ ] **Sin imports directos de LLM en dominio/aplicación**: `import anthropic`, `import groq`, `from google.generativeai import ...`, `import ollama` no aparecen en `domain/` ni en `application/`.
- [ ] **Sin instanciación directa de clientes LLM**: no hay `anthropic.Anthropic()`, `groq.Groq()` ni `genai.GenerativeModel()` fuera de los adaptadores secundarios y la capa de infraestructura.
- [ ] **LLMRequest con task_type correcto**: las llamadas al `LLMPort` especifican el `task_type` apropiado para que el Router pueda enrutar correctamente.
- [ ] **No se asume un proveedor concreto**: el código que llama al LLMPort no asume qué proveedor responderá — solo trabaja con `LLMResponse`.
- [ ] **Output LLM validado**: si el caso de uso espera JSON estructurado del LLM, valida el output con Pydantic antes de usarlo — nunca `json.loads()` sin capturar `JSONDecodeError`.

---

### 5. Tipos y calidad de código — bloqueante

- [ ] Todas las funciones públicas tienen anotaciones de tipo en parámetros y valor de retorno.
- [ ] No se usa `Any` salvo que esté justificado con un comentario.
- [ ] Los modelos Pydantic usan tipos concretos, no `dict` sin tipar.
- [ ] Las funciones async están marcadas con `async def`.
- [ ] El código pasaría `mypy backend/src/` con la configuración del proyecto.

---

### 6. Convenciones del proyecto — debe corregirse

Contrastar con la sección "Convenciones de Código" de `CLAUDE.md`:

- [ ] **Naming de puertos**: clases de puerto llevan sufijo `Port` (`TaskRepositoryPort`, no `TaskRepository`).
- [ ] **Naming de adaptadores**: clases de adaptador llevan sufijo `Adapter` (`JiraAdapter`, no `JiraClient`).
- [ ] **Naming de casos de uso**: clases de UC llevan sufijo `UseCase` (`EstimateTaskUseCase`).
- [ ] **Logging con structlog**: no hay `print()` ni `logging.getLogger()` directos.
- [ ] **Nombres en inglés**: variables, funciones, clases y módulos en inglés; los comentarios pueden estar en español.
- [ ] **Sin comentarios de "qué hace"**: los comentarios explican el "por qué", no el "qué". El código bien nombrado no necesita comentarios de descripción.

---

### 7. Rendimiento y coste LLM — sugerencias (no bloqueante)

- [ ] **task_type apropiado**: tareas simples (clasificación, extracción) no usan `REASONING` — eso enrutaría innecesariamente a Claude Sonnet.
- [ ] **Chunking RAG**: los documentos indexados usan el tamaño de chunk configurado (512 tokens con overlap 50). No hay chunks de 3 palabras ni de 10 páginas.
- [ ] **Paralelismo**: las llamadas independientes al LLM o al vector store se lanzan con `asyncio.gather()`, no secuencialmente.
- [ ] **Sin llamadas LLM duplicadas**: si el mismo prompt aparece en múltiples puntos del flujo, verificar si puede cachearse o reutilizarse.
- [ ] **max_tokens razonable**: los `LLMRequest` no pasan `max_tokens=4096` para tareas de clasificación que producen 10 tokens.

---

## Cómo reportar

```
[CATEGORÍA] [SEVERIDAD] fichero.py ~línea N
Problema: descripción concisa de qué está mal
Corrección: qué cambiar y por qué
```

Severidades:
- `BLOQUEANTE` — debe corregirse antes de cerrar la feature
- `DEBE-CORREGIRSE` — no bloqueante pero obligatorio según DoD
- `SUGERENCIA` — mejora de calidad o rendimiento, opcional

Al final, emitir un veredicto:
- **APROBADO** — no hay problemas bloqueantes ni de "debe corregirse"
- **APROBADO CON CAMBIOS MENORES** — solo sugerencias pendientes
- **RECHAZADO** — hay al menos un problema bloqueante o de "debe corregirse"
