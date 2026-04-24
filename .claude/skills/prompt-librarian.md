# Skill: prompt-librarian

## Cuándo se activa

Cuando se ha usado un prompt significativo durante el desarrollo. Se activa al finalizar una tarea donde el prompt haya sido clave para el resultado, o cuando el usuario pide explícitamente "añade este prompt a la biblioteca".

## Qué es un prompt significativo

Un prompt es significativo si cumple al menos uno de estos criterios:

- **Define arquitectura**: genera o modifica decisiones de diseño, ADRs, estructura del sistema
- **Resuelve un problema no trivial**: la solución no era obvia y el prompt fue determinante para llegar a ella
- **Genera documentación**: produce PRD, specs, ADRs, ARCHITECTURE.md u otro documento de proyecto
- **Genera código de producción**: crea o modifica módulos, adaptadores, casos de uso, tests
- **Sería útil reutilizar**: el patrón del prompt puede aplicarse a tareas futuras similares, en este proyecto o en otros

No son significativos: ajustes menores de formato, correcciones de typos, preguntas exploratorias sin resultado concreto.

## Proceso

### 1. Identificar la sección correcta en docs/PROMPTS.md

| Contenido del prompt | Sección |
|---------------------|---------|
| Definición de proyecto, PRD, specs | `1. Prompts de Definición de Proyecto` |
| Arquitectura, ADRs, diagramas | `2. Prompts de Arquitectura y Diseño` |
| Código Python / FastAPI / dominio | `3. Prompts de Desarrollo Backend` |
| Código TypeScript / React / UI | `4. Prompts de Desarrollo Frontend` |
| Tests, fixtures, mocks | `5. Prompts de Testing` |
| Documentación, README, CHANGELOG | `6. Prompts de Documentación` |
| Jira, Confluence, GitHub adapters | `7. Prompts de Integración` |
| LLM Router, RAG, embeddings, prompts de sistema | `8. Prompts de LLM y RAG` |

### 2. Crear la entrada en docs/PROMPTS.md

Añadir una nueva entrada con este formato exacto:

```markdown
### N.N [Nombre descriptivo del prompt]
**Fecha**: YYYY-MM-DD  
**Modelo**: claude-sonnet-4-6 / claude-haiku / ollama/llama3 / groq/llama3-8b  
**Resultado**: [una línea: qué produjo este prompt]  
**Ficheros generados/afectados**: [lista de ficheros, o "ninguno" si fue solo consulta]  

**Prompt**:

```
[texto completo del prompt, tal como se usó, sin editar]
```

**Notas**: [observaciones: variaciones que funcionan mejor, limitaciones conocidas, contexto necesario para reutilizarlo]
```

El número de entrada (N.N) es el siguiente disponible dentro de la sección. Si la sección tiene `1.1` y `1.2`, la nueva es `1.3`.

### 3. Actualizar la sección de Patrones si aplica

Si el prompt revela un **patrón reutilizable** (no solo un prompt concreto sino una estrategia general), añadirlo o actualizar la sección `9. Patrones y Buenas Prácticas`.

### 4. Intentar publicar en Confluence

Invocar el skill `confluence-publisher` para actualizar la página `06. Biblioteca de Prompts` con el contenido actualizado de `docs/PROMPTS.md`.

Si Confluence no está disponible, el skill confluence-publisher registrará el pendiente — no hay nada adicional que hacer aquí.

## Recomendación de reutilización

En las **Notas** de cada entrada, incluir siempre una línea explícita de reutilización:

- `Reutilizable en`: [otros contextos donde este prompt o patrón aplicaría]
- `Variación sugerida para X`: [si hay una versión alternativa para un caso ligeramente diferente]
- `No usar cuando`: [limitaciones o casos donde este prompt no funciona bien]

## Lo que NO hacer

- No resumir el prompt — copiar el texto exacto tal como se usó, incluyendo el contexto que se proporcionó
- No editar el prompt "para que quede mejor" en la biblioteca — la autenticidad es lo que lo hace útil
- No añadir prompts de exploración sin resultado concreto (preguntas de "¿cómo funciona X?")
- No duplicar una entrada si el prompt es muy similar a uno existente — en su lugar, añadir una nota de variación al existente
