# Metodología — PM con IA

**Versión**: 0.1  
**Fecha**: 2026-04-24  

---

## 1. Visión de la Metodología

Esta metodología adapta el marco ágil clásico (Scrum/Kanban) al desarrollo de software con LLMs como copilot activo. Reconoce que:

1. **El LLM es un miembro del equipo**, no solo una herramienta. Los prompts son artefactos de trabajo tan importantes como el código.
2. **El comportamiento no es determinista**. Los criterios de aceptación deben adaptarse para validar comportamientos probabilísticos.
3. **La documentación de prompts es conocimiento del proyecto**. Un prompt bien afinado tiene el mismo valor que un algoritmo bien optimizado.
4. **El ritmo de desarrollo es diferente**. Con un copilot de IA, la velocidad de generación de código aumenta pero aumenta también la necesidad de revisión y alineamiento de contexto.

---

## 2. Sprints de 1 Semana

### Justificación

Los sprints cortos de 1 semana son especialmente valiosos en desarrollo con IA:

- El contexto del LLM se "refresca" frecuentemente con retrospectivas y planning
- Los experimentos con prompts y modelos pueden evaluarse rápidamente
- Las decisiones de routing LLM (Ollama vs Claude) se validan con ciclos cortos
- La deuda técnica no acumula durante semanas

### Estructura del Sprint

```
Lunes     ─── Sprint Planning (1h)
               └── Revisión del backlog priorizado
               └── Selección de historias (capacidad estimada)
               └── Contexto briefing: actualizar CLAUDE.md si hay cambios relevantes
               
Martes-Jueves ─── Desarrollo
               └── Daily check-in personal (15 min): ¿qué hice, qué haré, hay bloqueadores?
               └── Documentar prompts significativos en docs/PROMPTS.md durante el trabajo
               
Viernes   ─── Sprint Review + Retrospectiva (1.5h)
               └── Demo de lo completado
               └── Métricas: puntos completados, velocidad, tasa de aceptación LLM
               └── Retrospectiva: ¿qué prompts funcionaron bien? ¿qué patrones emergieron?
               └── Actualizar docs/PROMPTS.md con prompts del sprint
               └── Publicar lección aprendida en Confluence "04. Lecciones Aprendidas"
```

---

## 3. User Stories para Features LLM

### Formato Extendido para Features con LLM

Las historias estándar ("Como X, quiero Y, para Z") se extienden con secciones específicas para comportamientos LLM:

```markdown
## Historia: [Nombre]

**Como** [rol del usuario]  
**Quiero** [acción deseada]  
**Para** [beneficio]  

### Criterios de Aceptación (Deterministas)
- [ ] El sistema acepta la entrada en el formato X
- [ ] El sistema persiste el resultado en PostgreSQL
- [ ] La API retorna el formato correcto
- [ ] Los errores de validación retornan 422 con detalle

### Criterios de Aceptación (No Deterministas — LLM)
- [ ] El output tiene el formato estructurado requerido (JSON schema: ...)
- [ ] En ≥ [N]/10 ejecuciones con el conjunto de prueba canónico, el output cumple [criterio de calidad]
- [ ] Si el output es inválido: [comportamiento de fallback definido]
- [ ] La latencia P95 es < [X] segundos

### Conjunto de Prueba Canónico
| Input | Output esperado (aproximado) | Criterio |
|-------|------------------------------|----------|
| ...   | ...                          | ...      |

### Prompt Template
(Referencia al prompt en docs/PROMPTS.md, sección X)

### LLM Router
- Tipo de tarea: [REASONING / GENERATION_LONG / CLASSIFICATION / EXTRACTION / SIMPLE_QA]
- Proveedor preferido: [Claude Sonnet / Claude Haiku / Ollama]
- Fallback: [comportamiento si el proveedor preferido no está disponible]
```

### Ejemplo

```markdown
## Historia: Estimación de Historia de Usuario con RAG

**Como** PM técnico  
**Quiero** obtener una estimación en puntos de Fibonacci para una historia  
**Para** planificar el sprint con datos basados en el historial real del equipo  

### Criterios de Aceptación (Deterministas)
- [ ] La API acepta `{ description: string, acceptance_criteria?: string }`
- [ ] La respuesta incluye `points`, `confidence`, `rationale`, `similar_tasks`
- [ ] `points` pertenece a la escala Fibonacci (1, 2, 3, 5, 8, 13, 21)
- [ ] Si el LLM devuelve output no parseable: retorna 422 con `{ error: "estimation_failed", detail: "..." }`
- [ ] La estimación se persiste en PostgreSQL con timestamp y provider usado

### Criterios de Aceptación (No Deterministas)
- [ ] En ≥ 8/10 ejecuciones con historias del backlog de prueba, `points` está dentro del ±1 nivel Fibonacci del consenso del equipo
- [ ] `confidence` está entre 0.0 y 1.0
- [ ] `similar_tasks` contiene ≥ 1 tarea real del proyecto cuando hay historial

### LLM Router
- Tipo de tarea: REASONING
- Proveedor preferido: Claude Sonnet
- Fallback: Ollama/llama3 con nota en `metadata.fallback_used: true`
```

---

## 4. Backlog y Priorización

### Niveles del Backlog

```
Product Backlog (sin plazo)
    └── Sprint Backlog (1 semana)
            └── Tareas de desarrollo (≤ 1 día cada una)
```

### Criterios de Priorización

1. **Valor para el usuario** (Impact): ¿cuántos usuarios se benefician y en qué medida?
2. **Dependencias técnicas**: ¿esta historia desbloquea otras?
3. **Riesgo LLM**: features con comportamiento LLM incierto se priorizan antes para validar early
4. **Deuda técnica**: se reserva 20% de la capacidad del sprint para deuda técnica

### Categorías de Tareas

| Tipo | Emoji | Descripción |
|------|-------|-------------|
| Feature | 🚀 | Nueva funcionalidad |
| Bug | 🐛 | Corrección de comportamiento incorrecto |
| Infra | 🔧 | Infraestructura, CI/CD, configuración |
| Docs | 📝 | Documentación |
| LLM Tuning | 🤖 | Refinamiento de prompts, calibración de router |
| Tech Debt | 💳 | Refactoring, mejoras de calidad |
| Research | 🔬 | Experimentos, evaluación de alternativas |

---

## 5. Gestión del Contexto del LLM

### El Problema del Contexto

A diferencia de un desarrollador humano que recuerda el proyecto, el LLM inicia cada sesión sin memoria. El `CLAUDE.md` es el mecanismo para transmitir contexto del proyecto entre sesiones.

### Protocolo de Sesión

**Al inicio de cada sesión de desarrollo**:
1. Revisar que `CLAUDE.md` está actualizado con los cambios del sprint anterior
2. Si hay decisiones recientes relevantes, añadir nota temporal al contexto
3. Comunicar al LLM el objetivo de la sesión y el sprint en curso

**Durante la sesión**:
1. Si el LLM parece haber "olvidado" una convención, refrescar el contexto con `@CLAUDE.md`
2. Documentar prompts que funcionan especialmente bien

**Al final de la sesión**:
1. Si se tomaron decisiones que afectan a sesiones futuras, actualizar `CLAUDE.md`
2. Añadir prompts significativos a `docs/PROMPTS.md`

### Qué va en CLAUDE.md vs PROMPTS.md

| Información | Destino |
|-------------|---------|
| Stack, estructura, convenciones | `CLAUDE.md` |
| Reglas permanentes de trabajo | `CLAUDE.md` |
| Prompts de desarrollo reutilizables | `docs/PROMPTS.md` |
| Prompts de definición del proyecto | `docs/PROMPTS.md` |
| Estado actual del sprint | Solo en la sesión (efímero) |

---

## 6. Testing de Comportamientos No Deterministas

### Estrategia de Testing LLM

```
Tests Deterministas (CI siempre)
    ├── Validación de formato de output (JSON schema)
    ├── Validación de tipos y rangos de valores
    ├── Tests de fallback (input inválido → comportamiento definido)
    └── Tests de integración con LLM mock (respuesta fija)

Tests Probabilísticos (CI semanal o manual)
    ├── Golden set evaluation: N inputs → tasa de aceptación
    ├── Regression: comparar con versión anterior del prompt
    └── Benchmark de calidad: Ollama vs Claude por tipo de tarea

Tests de Carga (pre-release)
    ├── Latencia P95 bajo carga
    └── Comportamiento del Circuit Breaker bajo fallos simulados
```

### Validación de Output LLM

```python
from pydantic import BaseModel, field_validator
from typing import Literal

FIBONACCI = {1, 2, 3, 5, 8, 13, 21}

class EstimationOutput(BaseModel):
    points: int
    confidence: float
    rationale: str
    similar_tasks: list[dict]

    @field_validator("points")
    def must_be_fibonacci(cls, v):
        if v not in FIBONACCI:
            raise ValueError(f"Points must be Fibonacci, got {v}")
        return v

    @field_validator("confidence")
    def must_be_normalized(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be [0,1], got {v}")
        return v
```

---

## 7. Métricas del Proceso

Al final de cada sprint, registrar:

| Métrica | Cómo medirla |
|---------|-------------|
| Velocidad (puntos completados) | Suma de puntos de historias done |
| Tasa de aceptación LLM | % de outputs válidos en golden set |
| Ratio Claude/Ollama | % de queries por proveedor (logs) |
| Coste LLM del sprint | $ según logs de tokens Anthropic |
| Prompts añadidos a biblioteca | Conteo de entradas nuevas en PROMPTS.md |
| Deuda técnica generada | Nuevas entradas DT-xxx en ADRs |

---

## 8. Gestión de Deuda Técnica

La deuda técnica se registra en el ADR correspondiente con formato `DT-NNN`:

```
DT-001: [Título breve]
Trigger: [condición que activa el trabajo de deuda]
Acción: [qué hay que hacer]
Estimación: [esfuerzo aproximado]
Prioridad: [baja / media / alta]
```

Se reserva el 20% de la capacidad de cada sprint para abordar deuda técnica de alta prioridad. La deuda de baja prioridad se revisa trimestralmente.
