# Skill: test-writer

## Cuándo se activa

Al crear o modificar cualquier módulo Python en `backend/src/`. Incluye: nuevas entidades de dominio, nuevos puertos, nuevos casos de uso, nuevos adaptadores (primarios o secundarios), cambios en el LLM Router o el RAG engine, cambios en modelos Pydantic.

## Principios

- Un test por comportamiento observable, no uno por función
- Los tests del dominio y la aplicación no llaman a ningún servicio externo — toda dependencia externa se mockea via los puertos
- Los tests son deterministas: el mismo input produce siempre el mismo resultado. Para features LLM, mockear el `LLMPort` con respuestas fijas
- Un test que falla debe indicar exactamente qué comportamiento está roto, sin ambigüedad

## Estructura de ficheros

Los tests espejan la estructura de `backend/src/`:

```
backend/src/domain/entities/task.py                 → tests/unit/domain/test_task.py
backend/src/domain/services/estimation_service.py   → tests/unit/domain/test_estimation_service.py
backend/src/application/use_cases/estimate_task.py  → tests/unit/application/test_estimate_task_uc.py
backend/src/adapters/primary/task_router.py         → tests/unit/adapters/primary/test_task_router.py
backend/src/adapters/secondary/jira_adapter.py      → tests/integration/adapters/test_jira_adapter.py
backend/src/infrastructure/llm_router/router.py     → tests/unit/infrastructure/test_llm_router.py
```

Si el directorio correspondiente en `tests/` no existe, crearlo con su `__init__.py`.

## Qué escribir para cada capa

### Entidades de dominio (`domain/entities/`)

```python
# Comportamientos a cubrir:
# 1. Creación con datos válidos → entidad correctamente inicializada
# 2. Invariantes de negocio: estimación de puntos debe ser Fibonacci, estado debe ser válido
# 3. Transiciones de estado: task.start() solo posible si status == "todo"
# 4. Serialización: la entidad serializa y deserializa sin pérdida de datos
# 5. Rechazo de inputs inválidos con ValueError descriptivo
```

### Puertos (interfaces abstractas) — no se testean directamente

Los puertos son ABCs sin implementación. Testear que los adaptadores los implementan correctamente usando el adaptador real o un mock que verifique la firma.

### Casos de uso (`application/use_cases/`)

Los casos de uso son el corazón del sistema — máxima cobertura aquí.

```python
# Todos los puertos se mockean con AsyncMock / MagicMock
# Comportamientos a cubrir:
# 1. Happy path: command válido → output con estructura correcta, repositorios llamados
# 2. Validación de command: campos requeridos ausentes → ValueError / CommandValidationError
# 3. Fallo de un puerto secundario: si el LLMPort falla, ¿el UC maneja la excepción correctamente?
# 4. Fallo del repositorio: si PostgreSQL no responde, ¿el UC propaga el error adecuado?
# 5. Lógica de negocio: verificar que el UC orquesta los puertos en el orden correcto
# 6. Output LLM inválido: si el LLMPort devuelve JSON malformado, el UC retorna error controlado
```

```python
@pytest.mark.asyncio
async def test_estimate_task_returns_fibonacci_points(
    mock_llm_port, mock_task_repo, mock_vector_store
):
    mock_llm_port.complete.return_value = LLMResponse(
        content='{"points": 5, "confidence": 0.8, "rationale": "Similar to past tasks"}',
        provider="mock",
        model="mock",
        input_tokens=100,
        output_tokens=50,
        latency_ms=200,
    )
    use_case = EstimateTaskUseCase(mock_llm_port, mock_task_repo, mock_vector_store)
    result = await use_case.execute(EstimateTaskCommand(description="Implement JWT auth"))
    assert result.points in {1, 2, 3, 5, 8, 13, 21}
    assert 0.0 <= result.confidence <= 1.0
```

### Adaptadores primarios — FastAPI routers (`adapters/primary/`)

```python
# Usar httpx.AsyncClient + TestClient de FastAPI
# Comportamientos a cubrir:
# 1. Happy path: request válido → 200/201 con body correcto
# 2. Validación Pydantic: request con campos inválidos → 422 con detalle
# 3. Propagación de errores del UC: si el UC lanza ApplicationError → 400/422 apropiado
# 4. Errores no esperados: si el UC lanza excepción no controlada → 500 sin exponer internals
# 5. Auth: endpoint protegido sin token → 401
```

### Adaptadores secundarios — integraciones externas (`adapters/secondary/`)

Estos van en `tests/integration/` y pueden usar:
- Mock HTTP con `pytest-httpx` (preferido para CI)
- Servicio real en local con `@pytest.mark.integration` (opcional, no en CI por defecto)

```python
# Comportamientos a cubrir:
# 1. Happy path: llamada al servicio → respuesta parseada correctamente
# 2. Error 4xx del servicio: → excepción tipada del dominio (no raw httpx.HTTPStatusError)
# 3. Timeout de red: → excepción tipada del dominio
# 4. Circuit Breaker: tras N fallos, la siguiente llamada falla rápido sin contactar el servicio
# 5. Respuesta inesperada (schema cambiado): → error de parsing con mensaje descriptivo
```

### LLM Router (`infrastructure/llm_router/`)

```python
# Comportamientos a cubrir:
# 1. Routing correcto: TaskType.REASONING → AnthropicAdapter llamado
# 2. Routing correcto: TaskType.CLASSIFICATION → GroqAdapter llamado
# 3. Fallback: si AnthropicAdapter falla → siguiente en la cadena es llamado
# 4. Fallback en cadena: Claude falla → Groq falla → Ollama es llamado
# 5. Circuit Breaker abierto: el adapter no es contactado, se va directo al fallback
# 6. LLM_MODE=local: todos los tipos → OllamaAdapter
# 7. LLM_MODE=budget: REASONING → Claude, resto → Groq
```

### RAG Engine (`infrastructure/rag/`)

```python
# Comportamientos a cubrir:
# 1. Indexación: documento → chunks del tamaño correcto con metadata
# 2. Embedding: chunks → vectores de 768 dimensiones (nomic-embed-text)
# 3. Búsqueda: query → top-K chunks ordenados por similitud
# 4. Búsqueda vacía: query sin resultados similares → lista vacía (no error)
# 5. ChromaDB no disponible: → CircuitOpenError propagado correctamente
```

## Fixtures y mocks

Los fixtures reutilizables van en `tests/conftest.py`:

```python
# @pytest.fixture: mock de LLMPort (AsyncMock) con respuesta de estimación predefinida
# @pytest.fixture: mock de TaskRepositoryPort (AsyncMock) con lista de tareas de ejemplo
# @pytest.fixture: mock de VectorStorePort (AsyncMock) con chunks de ejemplo
# @pytest.fixture: mock de JiraPort (AsyncMock)
# @pytest.fixture: mock de ConfluencePort (AsyncMock)
# @pytest.fixture: FastAPI TestClient con todos los ports mockeados inyectados
# @pytest.fixture: tarea de ejemplo con todos los campos requeridos
# @pytest.fixture: sprint de ejemplo activo
# @pytest.fixture: configuración de entorno de test (LLM_MODE=local, sin API keys reales)
```

Para mockear llamadas async usar `pytest-asyncio` con `AsyncMock`:

```python
@pytest.mark.asyncio
async def test_create_task_persists_to_repository(mock_task_repo, mock_llm_port):
    mock_task_repo.save.return_value = Task(id=uuid4(), title="Test task", ...)
    use_case = CreateTaskUseCase(task_repo=mock_task_repo)
    result = await use_case.execute(CreateTaskCommand(title="Test task", ...))
    mock_task_repo.save.assert_awaited_once()
    assert result.title == "Test task"
```

## Cobertura mínima

Antes de dar un módulo por completo, verificar que se cubren al menos:
- El camino feliz principal
- Al menos un caso de fallo de cada puerto del que depende el UC
- Al menos un caso de input inválido o en el límite

Si la cobertura de dominio y aplicación es inferior al 80%, añadir los tests que faltan antes de considerar el trabajo terminado. Ver `docs/DEFINITION_OF_DONE.md`.

## Lo que NO hacer

- No testear que Pydantic valida correctamente sus propios campos internos — confiar en la librería
- No testear implementaciones privadas (`_metodo`) — testear el comportamiento público
- No crear tests que solo verifican que una función fue llamada sin verificar el resultado
- No usar `time.sleep()` en tests — si hay lógica de retry/backoff, mockear el tiempo
- No importar `anthropic`, `groq` o `google.generativeai` en tests del dominio o aplicación — solo los ports abstractos
- No hacer llamadas reales a APIs externas en tests sin marcar `@pytest.mark.integration` y asegurarse de que están excluidos de CI
