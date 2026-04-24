# ADR-003 — Circuit Breaker en Integraciones Externas

**Estado**: Aceptado  
**Fecha**: 2026-04-24  
**Autor**: Marcos Vese  

---

## Contexto

PM Copilot depende de múltiples servicios externos que pueden fallar de forma independiente:

| Servicio | Tipo de fallo potencial |
|----------|------------------------|
| Anthropic Claude API | Rate limiting, downtime, latencia alta, errores de red |
| Ollama local | Proceso caído, modelo no cargado, timeout |
| Jira API | Throttling (Atlassian limita a 10 req/s), authn expirado |
| Confluence API | Igual que Jira |
| GitHub API | Rate limiting (5000 req/h), downtime |
| ChromaDB | Proceso caído, disco lleno |
| PostgreSQL | Conexiones agotadas, fallo del servidor |

Sin protección, un fallo en Jira podría bloquear la creación de tareas completa, aunque el resto del sistema funcione. Una llamada colgante a Claude podría bloquear el thread del servidor durante 60 segundos. Un retry storm podría agravar el problema.

---

## Decisión

Implementar el patrón **Circuit Breaker** en todos los adaptadores secundarios que llaman a servicios externos, usando la biblioteca `tenacity` para retry logic y un circuit breaker state machine propio (o `circuitbreaker` si se prefiere una biblioteca dedicada).

---

## Comportamiento del Circuit Breaker

### Estados

```
        [CERRADO] ──(N fallos en ventana T)──▶ [ABIERTO]
            ▲                                       │
            │                                       │ (timeout T_reset)
            │                                       ▼
         (éxito)                              [SEMI-ABIERTO]
            └──────────────────────────────── (1 llamada de prueba)
```

- **CERRADO**: funcionamiento normal. Cuenta fallos consecutivos.
- **ABIERTO**: rechaza todas las llamadas inmediatamente con `CircuitOpenError`. No intenta conectar al servicio.
- **SEMI-ABIERTO**: después del timeout, permite una llamada de prueba. Si tiene éxito → CERRADO. Si falla → ABIERTO.

### Parámetros por Servicio

| Servicio | Fallos para abrir | Timeout reset | Fallback |
|----------|------------------|---------------|---------|
| Claude API | 3 en 60s | 30s | Ollama Router |
| Ollama | 3 en 30s | 15s | Error gracioso |
| Jira API | 5 en 120s | 60s | Tarea solo en DB local |
| Confluence API | 5 en 120s | 60s | Error gracioso |
| GitHub API | 5 en 120s | 60s | Error gracioso |
| ChromaDB | 3 en 30s | 20s | LLM sin contexto RAG |
| PostgreSQL | 3 en 15s | 10s | Error 503 |

### Estrategia de Retry (previa al Circuit Breaker)

Antes de contar un fallo, se aplica retry con backoff exponencial:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((NetworkError, TimeoutError)),
    reraise=True,
)
```

Solo se hacen retries en errores transitorios (red, timeout). Los errores de autenticación (401, 403) y validación (400) no se reintentan.

---

## Comportamientos de Fallback

### Fallback Claude → Ollama (LLM Router)

```python
class LLMRouter:
    async def complete(self, prompt: str, task_type: TaskType) -> LLMResponse:
        try:
            if self.claude_circuit.is_closed and task_type.requires_reasoning:
                return await self.claude_adapter.complete(prompt)
        except CircuitOpenError:
            pass  # fall through to Ollama
        return await self.ollama_adapter.complete(prompt)
```

### Fallback Jira → Local Only

Si Jira no está disponible, la tarea se crea en PostgreSQL local con `sync_status=PENDING`. Un job de background reintentará la sincronización cuando el circuit se cierre.

### Fallback ChromaDB → LLM sin RAG

Si ChromaDB no responde, el sistema responde con el LLM sin contexto enriquecido, indicando al usuario que la respuesta no tiene contexto del proyecto.

```python
try:
    context_chunks = await self.vector_store.search(query, top_k=5)
except CircuitOpenError:
    context_chunks = []
    metadata["rag_available"] = False
```

---

## Observabilidad

Cada cambio de estado del circuit breaker debe:
1. Emitir un log estructurado con nivel WARNING/ERROR
2. Incrementar un counter de métricas (`circuit_state_changes_total{service, from_state, to_state}`)
3. Los dashboards de Railway deben mostrar estos contadores

---

## Implementación

```python
# infrastructure/circuit_breaker.py
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, TypeVar, Any
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitOpenError(Exception):
    pass

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3
    reset_timeout_seconds: int = 30
    half_open_calls: int = 1

class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: datetime | None = None

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError(f"Circuit {self.name} is OPEN")
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(
            seconds=self.config.reset_timeout_seconds
        )
```

---

## Consecuencias

### Positivas
- El sistema degrada graciosamente cuando fallan servicios externos
- Protege los servicios externos de retry storms
- Mejora la resiliencia y el tiempo de respuesta percibido (fail fast en lugar de timeout)
- El fallback Claude→Ollama garantiza continuidad del servicio LLM

### Negativas / Trade-offs
- Complejidad adicional en adaptadores
- Los timeouts y umbrales deben calibrarse con datos reales de producción
- El estado del circuit breaker es en memoria — en caso de restart, el circuit comienza CERRADO

### Deuda Técnica
- Si se despliegan múltiples instancias del backend, el estado del circuit breaker debería compartirse via Redis para coordinar los estados entre instancias
