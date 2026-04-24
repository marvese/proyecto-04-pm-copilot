# ADR-005 — LLM Router: Capa de Abstracción LLM con Routing Inteligente

**Estado**: Aceptado  
**Fecha**: 2026-04-24  
**Última revisión**: 2026-04-24  
**Autor**: Marcos Vese  

---

## Contexto

PM Copilot necesita capacidades LLM para múltiples tareas con características muy distintas en cuanto a complejidad, latencia y coste:

| Tarea | Complejidad | Latencia requerida | Coste |
|-------|------------|-------------------|-------|
| Estimar historia de usuario | Alta (razonamiento) | Media (< 5s) | Alto |
| Generar informe de sprint | Alta (generación larga) | Baja (puede tardar) | Alto |
| Resumir PR para revisión | Media-alta | Media | Medio |
| Responder query RAG simple | Baja-Media | Baja | Bajo |
| Clasificar tipo de consulta | Baja (clasificación) | Muy baja (< 1s) | Muy bajo |
| Extraer entidades de tarea | Media | Baja | Bajo |

Ningún proveedor único es óptimo para todos los casos. Usar siempre Claude Sonnet maximiza la calidad pero dispara el coste y la latencia. Usar siempre Ollama local elimina el coste pero sacrifica calidad en tareas complejas y no escala en producción.

El sistema necesita una capa de abstracción que:
- Oculte el proveedor al dominio (intercambiabilidad)
- Enrute cada tarea al proveedor óptimo según coste/calidad/velocidad
- Soporte múltiples proveedores simultáneamente con fallback en cadena
- Permita trabajar completamente local (gratis) durante el desarrollo

---

## Decisión

Implementar un **LLM Router** como componente de infraestructura con cuatro adaptadores:

1. **Anthropic** (Claude Sonnet/Haiku) — calidad máxima, producción
2. **Ollama** (llama3, Mistral) — gratuito, local, desarrollo y fallback final
3. **Groq** (llama3, Mixtral) — velocidad extrema, muy bajo coste, producción en tareas simples
4. **Google Gemini** (Flash, Pro) — alternativa multimodal con tier gratuito generoso

El router expone un único `LLMPort` al dominio. Los casos de uso no saben qué proveedor ejecuta su solicitud.

---

## Adaptadores Disponibles

### 1. Anthropic — Claude Sonnet / Haiku

**Caso de uso óptimo**: razonamiento complejo, estimaciones, generación de documentos largos, análisis de riesgos, cualquier tarea donde la calidad del output sea crítica.

| Modelo | Coste input | Coste output | Contexto | Velocidad |
|--------|------------|-------------|---------|-----------|
| claude-sonnet-4-6 | ~$3/M tokens | ~$15/M tokens | 200K tokens | Media |
| claude-haiku-4-5 | ~$0.25/M tokens | ~$1.25/M tokens | 200K tokens | Alta |

**Cuándo usarlo**:
- `REASONING`: estimaciones, análisis de dependencias, planificación de sprint
- `GENERATION_LONG`: informes completos, documentación técnica, PRD
- Cualquier tarea donde el output sea presentado directamente al usuario sin revisión

**Limitaciones**:
- Coste por token el más alto del portfolio
- Rate limits en plan básico (límites por minuto y por día)
- Requiere conexión a internet — no disponible en entornos air-gapped

**Fallback**: Claude Haiku → Groq → Ollama

---

### 2. Ollama — llama3 / Mistral (local)

**Caso de uso óptimo**: desarrollo local con coste cero, tareas simples repetitivas que no justifican coste de API, fallback de último recurso cuando todos los proveedores cloud fallan.

| Modelo | Coste | Contexto | RAM requerida | Velocidad |
|--------|-------|---------|--------------|-----------|
| llama3 (8B) | Gratis | 8K tokens | ~8GB VRAM / 16GB RAM | Media-baja |
| llama3 (70B) | Gratis | 8K tokens | ~48GB RAM | Baja |
| mistral (7B) | Gratis | 32K tokens | ~8GB VRAM / 16GB RAM | Media |

**Cuándo usarlo**:
- `LLM_MODE=local` — todo el desarrollo local
- Fallback final cuando todos los proveedores cloud están en estado OPEN
- Tareas de extracción simple y clasificación donde la calidad exacta no es crítica

**Limitaciones**:
- Calidad inferior a Claude y Groq en razonamiento complejo
- Requiere hardware local suficiente (16GB RAM mínimo recomendado)
- No disponible en Railway sin instancia con GPU — solo usado como fallback local
- Contexto limitado en modelos 8B

**Fallback**: ninguno (último eslabón de la cadena)

---

### 3. Groq — llama3 / Mixtral

**Caso de uso óptimo**: tareas que requieren velocidad extrema en producción con muy bajo coste — clasificaciones, extracciones, queries RAG simples, cualquier tarea repetitiva de volumen alto.

| Modelo | Coste input | Coste output | Contexto | Velocidad |
|--------|------------|-------------|---------|-----------|
| llama3-8b-8192 | ~$0.05/M tokens | ~$0.08/M tokens | 8K tokens | Muy alta (500+ tokens/s) |
| llama3-70b-8192 | ~$0.59/M tokens | ~$0.79/M tokens | 8K tokens | Alta |
| mixtral-8x7b-32768 | ~$0.24/M tokens | ~$0.24/M tokens | 32K tokens | Alta |

**Cuándo usarlo**:
- `CLASSIFICATION`: clasificar intenciones de queries del usuario
- `EXTRACTION`: extraer entidades (nombres de tareas, fechas, responsables) de texto
- `SIMPLE_QA`: responder queries RAG donde el contexto está completamente en el prompt
- Cualquier tarea de volumen alto donde la latencia sea crítica

**Limitaciones**:
- Rate limits agresivos en el tier gratuito (30 req/min, 14.400 req/día)
- Contexto limitado (8K tokens en modelos más baratos) — no apto para documentos largos
- Los modelos son open-source corriendo en hardware de Groq — calidad inferior a Claude en razonamiento
- Sin soporte multimodal

**Fallback**: Ollama local

---

### 4. Google Gemini — Flash / Pro

**Caso de uso óptimo**: tareas multimodales (análisis de imágenes, diagramas), contexto muy largo que supere los límites de otros proveedores, o como alternativa cuando Claude y Groq no están disponibles.

| Modelo | Coste input | Coste output | Contexto | Capacidades especiales |
|--------|------------|-------------|---------|----------------------|
| gemini-2.0-flash | ~$0.075/M tokens | ~$0.30/M tokens | 1M tokens | Velocidad, multimodal |
| gemini-2.0-pro | ~$1.25/M tokens | ~$5/M tokens | 2M tokens | Razonamiento, multimodal |
| gemini-1.5-flash (free tier) | Gratis hasta 1500 req/día | Gratis | 1M tokens | Tier gratuito generoso |

**Cuándo usarlo**:
- Análisis de diagramas o imágenes (arquitectura, wireframes) — capacidad multimodal
- Documentos de contexto muy largo que superen los 200K tokens de Claude
- `gemini-1.5-flash` en tier gratuito para desarrollo como alternativa a Ollama cuando Ollama no está disponible
- Tareas de `GENERATION_LONG` como alternativa de coste cuando Claude es demasiado caro

**Limitaciones**:
- El tier gratuito tiene restricciones geográficas (no disponible en todos los países de la UE)
- Calidad en razonamiento ligeramente inferior a Claude Sonnet en benchmarks de código
- La integración multimodal requiere adaptador extendido con `EmbeddingPort` separado
- Los modelos Pro tienen latencia más alta que Groq

**Fallback**: Groq → Ollama

---

## Arquitectura del LLM Router

```
LLMPort (domain interface)
    └── LLMRouter (infrastructure implementation)
            │
            ├── TaskClassifier (determinista, sin LLM)
            │     ├── "reasoning"        → AnthropicAdapter (claude-sonnet-4-6)
            │     ├── "generation_long"  → AnthropicAdapter (claude-sonnet-4-6)
            │     ├── "classification"   → GroqAdapter (llama3-8b)
            │     ├── "extraction"       → GroqAdapter (llama3-8b)
            │     └── "simple_qa"        → GroqAdapter (mixtral) / GeminiAdapter (flash)
            │
            ├── AnthropicAdapter
            │     ├── Circuit Breaker (threshold: 3, reset: 30s)
            │     ├── anthropic SDK
            │     └── fallback → AnthropicAdapter(haiku) → GroqAdapter
            │
            ├── GroqAdapter
            │     ├── Circuit Breaker (threshold: 5, reset: 30s)
            │     ├── groq SDK / httpx
            │     └── fallback → OllamaAdapter
            │
            ├── GeminiAdapter
            │     ├── Circuit Breaker (threshold: 5, reset: 60s)
            │     ├── google-generativeai SDK
            │     └── fallback → GroqAdapter
            │
            └── OllamaAdapter (fallback final)
                  ├── Circuit Breaker (threshold: 3, reset: 15s)
                  ├── httpx → http://localhost:11434
                  └── fallback → CircuitOpenError (sin más opciones)
```

---

## Reglas de Routing

### Por tipo de tarea

```python
class TaskType(Enum):
    REASONING = "reasoning"              # Estimación, análisis, planificación
    GENERATION_LONG = "generation_long"  # Informes completos, documentación
    CLASSIFICATION = "classification"    # Clasificar intención del usuario
    EXTRACTION = "extraction"            # Extraer entidades de texto
    SIMPLE_QA = "simple_qa"             # Queries RAG con contexto en el prompt

class Provider(Enum):
    CLAUDE_SONNET = "claude_sonnet"
    CLAUDE_HAIKU = "claude_haiku"
    GROQ_LLAMA3 = "groq_llama3"
    GROQ_MIXTRAL = "groq_mixtral"
    GEMINI_FLASH = "gemini_flash"
    GEMINI_PRO = "gemini_pro"
    OLLAMA_LLAMA3 = "ollama_llama3"
    OLLAMA_MISTRAL = "ollama_mistral"

ROUTING_RULES: dict[TaskType, Provider] = {
    TaskType.REASONING:       Provider.CLAUDE_SONNET,
    TaskType.GENERATION_LONG: Provider.CLAUDE_SONNET,
    TaskType.CLASSIFICATION:  Provider.GROQ_LLAMA3,
    TaskType.EXTRACTION:      Provider.GROQ_LLAMA3,
    TaskType.SIMPLE_QA:       Provider.GROQ_MIXTRAL,
}

FALLBACK_CHAIN: dict[Provider, Provider | None] = {
    Provider.CLAUDE_SONNET:  Provider.CLAUDE_HAIKU,
    Provider.CLAUDE_HAIKU:   Provider.GROQ_LLAMA3,
    Provider.GROQ_LLAMA3:    Provider.OLLAMA_LLAMA3,
    Provider.GROQ_MIXTRAL:   Provider.OLLAMA_MISTRAL,
    Provider.GEMINI_FLASH:   Provider.GROQ_LLAMA3,
    Provider.GEMINI_PRO:     Provider.CLAUDE_SONNET,
    Provider.OLLAMA_LLAMA3:  None,  # fin de la cadena
    Provider.OLLAMA_MISTRAL: None,  # fin de la cadena
}
```

### Por entorno

```python
# .env
LLM_MODE=local        # Fuerza Ollama para todo (desarrollo sin costes)
LLM_MODE=production   # Aplica ROUTING_RULES + FALLBACK_CHAIN
LLM_MODE=budget       # Prioriza Groq y Gemini free tier, Claude solo para REASONING
LLM_MODE=auto         # production con fallback automático si proveedor no disponible
```

### Configuración: settings.yml de ejemplo

```yaml
llm_router:
  mode: auto  # local | production | budget | auto

  routing_rules:
    reasoning: claude_sonnet
    generation_long: claude_sonnet
    classification: groq_llama3
    extraction: groq_llama3
    simple_qa: groq_mixtral

  providers:
    claude_sonnet:
      adapter: anthropic
      model: claude-sonnet-4-6
      circuit_breaker:
        failure_threshold: 3
        reset_timeout_seconds: 30
      fallback: claude_haiku

    claude_haiku:
      adapter: anthropic
      model: claude-haiku-4-5-20251001
      circuit_breaker:
        failure_threshold: 3
        reset_timeout_seconds: 30
      fallback: groq_llama3

    groq_llama3:
      adapter: groq
      model: llama3-8b-8192
      circuit_breaker:
        failure_threshold: 5
        reset_timeout_seconds: 30
      fallback: ollama_llama3

    groq_mixtral:
      adapter: groq
      model: mixtral-8x7b-32768
      circuit_breaker:
        failure_threshold: 5
        reset_timeout_seconds: 30
      fallback: ollama_mistral

    gemini_flash:
      adapter: gemini
      model: gemini-2.0-flash
      circuit_breaker:
        failure_threshold: 5
        reset_timeout_seconds: 60
      fallback: groq_llama3

    gemini_pro:
      adapter: gemini
      model: gemini-2.0-pro
      circuit_breaker:
        failure_threshold: 3
        reset_timeout_seconds: 60
      fallback: claude_sonnet

    ollama_llama3:
      adapter: ollama
      model: llama3
      base_url: http://localhost:11434
      circuit_breaker:
        failure_threshold: 3
        reset_timeout_seconds: 15
      fallback: null  # último recurso

    ollama_mistral:
      adapter: ollama
      model: mistral
      base_url: http://localhost:11434
      circuit_breaker:
        failure_threshold: 3
        reset_timeout_seconds: 15
      fallback: null

  mode_overrides:
    local:
      reasoning: ollama_llama3
      generation_long: ollama_llama3
      classification: ollama_llama3
      extraction: ollama_llama3
      simple_qa: ollama_llama3
    budget:
      reasoning: claude_sonnet      # solo donde es imprescindible
      generation_long: gemini_flash  # contexto largo, precio bajo
      classification: groq_llama3
      extraction: groq_llama3
      simple_qa: groq_llama3
```

### Criterios de clasificación de tarea

La clasificación es determinista (no usa LLM para evitar recursión):
- Tipo de comando explícito: `/estimate` → REASONING, `/report` → GENERATION_LONG
- Flag en `LLMRequest.task_type` establecido por el caso de uso
- Longitud del output esperado: si `max_tokens > 2000` → GENERATION_LONG
- Heurística de complejidad: presencia de instrucciones multi-step en el system prompt

---

## Embeddings: nomic-embed-text

Los embeddings están separados del LLM de generación y tienen su propio puerto:

```python
class EmbeddingPort(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def dimensions(self) -> int: ...
```

**Implementación**: `NomicEmbedTextAdapter` via Ollama API (`/api/embeddings`)

**Modelo**: `nomic-embed-text` — 768 dimensiones, contexto de 8192 tokens

**Por qué `nomic-embed-text`**:
- Completamente local — sin coste por token, sin dependencia de API externa
- MTEB benchmark: comparable a `text-embedding-ada-002` en recuperación semántica
- Determinista — el mismo texto produce siempre el mismo vector
- Soporte nativo en Ollama — mismo runtime que los modelos de generación
- Buena calidad bilingüe español/inglés para la documentación mixta del proyecto

**Alternativas descartadas**:
- `text-embedding-ada-002` / `text-embedding-3-small`: coste por token, dependencia de OpenAI
- `all-MiniLM-L6-v2`: menor calidad, requiere runtime diferente a Ollama

---

## Interfaz del Puerto LLM

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator

@dataclass
class LLMRequest:
    prompt: str
    system_prompt: str | None = None
    task_type: TaskType = TaskType.SIMPLE_QA
    max_tokens: int = 2048
    temperature: float = 0.7
    stream: bool = False
    preferred_provider: Provider | None = None  # override del routing

@dataclass
class LLMResponse:
    content: str
    provider: str          # "claude-sonnet-4-6", "groq/llama3-8b", "ollama/llama3", etc.
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    rag_used: bool = False
    fallback_used: bool = False
    fallback_reason: str | None = None

class LLMPort(ABC):
    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse: ...

    @abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncIterator[str]: ...
```

---

## Cómo Añadir un Nuevo Adaptador

El LLM Router está diseñado para que añadir un nuevo proveedor sea un cambio contenido en la capa de infraestructura, sin tocar el dominio ni los casos de uso.

### Pasos para registrar un nuevo adaptador

**1. Implementar la interfaz `LLMAdapterBase`**

```python
# backend/src/infrastructure/llm_router/adapters/nuevo_proveedor_adapter.py
from .base import LLMAdapterBase
from ..ports import LLMRequest, LLMResponse

class NuevoProveedorAdapter(LLMAdapterBase):
    def __init__(self, api_key: str, model: str):
        self.client = NuevoProveedorClient(api_key=api_key)
        self.model = model

    async def complete(self, request: LLMRequest) -> LLMResponse:
        response = await self.client.generate(
            model=self.model,
            prompt=request.prompt,
            system=request.system_prompt,
            max_tokens=request.max_tokens,
        )
        return LLMResponse(
            content=response.text,
            provider="nuevo_proveedor",
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=response.latency_ms,
        )

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        async for chunk in self.client.stream(...):
            yield chunk.text
```

**2. Añadir al enum `Provider`**

```python
# backend/src/infrastructure/llm_router/router.py
class Provider(Enum):
    ...
    NUEVO_PROVEEDOR = "nuevo_proveedor"
```

**3. Registrar en el contenedor de dependencias**

```python
# backend/src/infrastructure/config/container.py
def build_llm_router(settings: Settings) -> LLMRouter:
    adapters = {
        Provider.NUEVO_PROVEEDOR: NuevoProveedorAdapter(
            api_key=settings.nuevo_proveedor_api_key,
            model=settings.nuevo_proveedor_model,
        ),
        ...
    }
    ...
```

**4. Añadir configuración en `settings.yml`**

```yaml
providers:
  nuevo_proveedor_model:
    adapter: nuevo_proveedor
    model: nombre-del-modelo
    circuit_breaker:
      failure_threshold: 3
      reset_timeout_seconds: 30
    fallback: ollama_llama3
```

**5. Añadir variables de entorno en `.env`**

```bash
NUEVO_PROVEEDOR_API_KEY=sk-...
```

**6. Escribir tests del adaptador**

```python
# backend/tests/integration/test_nuevo_proveedor_adapter.py
@pytest.mark.integration
async def test_complete_returns_valid_response():
    adapter = NuevoProveedorAdapter(api_key="test-key", model="test-model")
    # Test contra mock httpx o servicio real si disponible
    ...

async def test_circuit_breaker_opens_after_failures():
    # Verificar que el circuit breaker abre tras N fallos
    ...
```

**7. Actualizar `docs/ADR-005-llm-router.md`**

Documentar el nuevo proveedor en la sección "Adaptadores Disponibles" con su caso de uso, costes, limitaciones y cuándo usarlo.

### Checklist para nuevo adaptador

- [ ] Implementa `LLMAdapterBase` con `complete()` y `stream()`
- [ ] Retorna `LLMResponse` con todos los campos (incluyendo `latency_ms`)
- [ ] Tiene Circuit Breaker configurado
- [ ] Está registrado en el DI container
- [ ] Tiene entrada en `settings.yml` con `fallback` definido
- [ ] La API key está en `.env` (nunca hardcodeada)
- [ ] Tests unitarios con mock del cliente HTTP
- [ ] Tests de integración (marcados con `@pytest.mark.integration`)
- [ ] Documentado en este ADR

---

## Consecuencias

### Positivas
- Los casos de uso son completamente agnósticos al proveedor LLM
- Portfolio de cuatro proveedores cubre todos los escenarios de coste/velocidad/calidad
- Fallback en cadena garantiza máxima disponibilidad del servicio LLM
- Reducción de costes estimada: 60-75% vs usar siempre Claude Sonnet (tasks simples → Groq)
- Desarrollo sin coste con `LLM_MODE=local` (Ollama)
- El modo `budget` permite usar Gemini free tier para reducir coste a prácticamente cero
- Añadir nuevos proveedores es un cambio en infraestructura — no toca el dominio

### Negativas / Trade-offs
- Mayor complejidad de configuración y mantenimiento (4 SDKs, 4 Circuit Breakers)
- El TaskClassifier debe ser determinista y sin LLM — es la pieza más delicada
- Los benchmarks de calidad por tarea deben mantenerse para ajustar las reglas de routing
- `nomic-embed-text` requiere Ollama en local — en CI necesita mock o servicio alternativo
- Los rate limits de Groq en tier gratuito pueden ser un cuello de botella en producción

### Deuda Técnica

- **DT-003**: Benchmark formal de calidad por tipo de tarea (Groq vs Claude vs Gemini) con datos reales del proyecto — calibrar las reglas de routing con datos empíricos
- **DT-004**: Evaluar Groq vs Claude Haiku en cost/quality para tareas de clasificación con volumen real
- **DT-005**: Implementar métricas de coste acumulado por proveedor para optimizar el routing rules basándose en el gasto real
- **DT-006**: Considerar Gemini multimodal para análisis de diagramas de arquitectura — requiere extender `LLMRequest` con soporte de imagen
