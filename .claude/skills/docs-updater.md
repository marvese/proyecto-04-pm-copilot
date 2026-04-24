# Skill: docs-updater

## Cuándo se activa

Tras cualquier cambio significativo en el proyecto: nueva arquitectura o modificación de la existente, incorporación o eliminación de dependencias, cambio en convenciones de código, nueva decisión técnica relevante, o cualquier cambio que afecte a cómo un desarrollador nuevo entendería o arrancaría el proyecto.

## Qué hacer

### 1. Evaluar si CLAUDE.md necesita actualización

Revisar si el cambio afecta a alguna de estas secciones:

- **Stack** — ¿se ha añadido, eliminado o sustituido alguna dependencia o herramienta?
- **LLM & RAG** — ¿se ha añadido un nuevo adaptador, cambiado un modelo, modificado las reglas de routing?
- **Estructura de carpetas** — ¿se ha creado un módulo, paquete o directorio nuevo no previsto?
- **Variables de entorno** — ¿se ha añadido una variable nueva que el desarrollador necesita configurar?
- **Integraciones Activas** — ¿ha cambiado el estado de alguna integración (Jira, GitHub, Groq, Gemini)?
- **Convenciones de código** — ¿se ha establecido un patrón nuevo que debe seguirse en adelante?
- **Reglas de trabajo** — ¿se ha acordado una restricción o práctica nueva?
- **Deuda técnica conocida** — ¿se ha resuelto un ítem DT-xxx o aparecido uno nuevo?
- **Skills activos** — ¿se ha añadido, modificado o eliminado un skill en `.claude/skills/`?

Si alguna sección está desactualizada, actualizarla. No añadir secciones nuevas salvo que el cambio lo justifique explícitamente.

### 2. Evaluar si se debe crear un nuevo ADR

Crear un ADR en `docs/ADR-NNN-titulo.md` cuando el cambio implique una **decisión técnica con alternativas consideradas y consecuencias no triviales**. Criterios:

- Se elige entre dos o más opciones de diseño o tecnología
- La decisión afecta a más de un módulo o tiene impacto en el largo plazo
- Revertir la decisión costaría esfuerzo significativo

El nombre del fichero usa el siguiente número de secuencia disponible (revisar `docs/` para determinarlo). Estructura:

```markdown
# ADR-NNN — Título de la decisión

**Estado**: Aceptado
**Fecha**: YYYY-MM-DD

## Contexto
[Por qué fue necesario tomar esta decisión]

## Opciones consideradas
[Al menos dos opciones con pros/contras]

## Decisión
[Qué se eligió y por qué]

## Consecuencias
[Positivas, negativas y deuda técnica si aplica]
```

### 3. Actualizar CHANGELOG.md

Si `CHANGELOG.md` no existe, crearlo con la cabecera estándar de Keep a Changelog:

```markdown
# Changelog

Todos los cambios notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).
```

Añadir una entrada bajo `## [Unreleased]` con el formato:

```markdown
## [Unreleased]

### Added
- [descripción de lo añadido]

### Changed
- [descripción de lo modificado]

### Fixed
- [descripción de lo corregido]

### Removed
- [descripción de lo eliminado]
```

Solo incluir las subsecciones que apliquen. No incluir subsecciones vacías.

### 4. Verificar README.md

Si `README.md` existe, comprobar que:
- Los comandos de instalación y ejecución siguen siendo válidos
- Las dependencias listadas coinciden con `pyproject.toml`
- La descripción del proyecto sigue siendo precisa

Si README.md no existe aún, no crearlo (se crea cuando el proyecto tenga código funcionando).

### 5. Publicar en Confluence (nuevo respecto a proyecto-03)

Tras cualquier cambio significativo en documentación, invocar el skill `confluence-publisher` para sincronizar la página correspondiente:

| Documento modificado | Página Confluence |
|---------------------|------------------|
| `docs/ADR-*.md` | `03. Arquitectura y Decisiones Técnicas` |
| `docs/METODOLOGIA.md` | `01. Metodología PM con IA` |
| Lecciones aprendidas | `04. Lecciones Aprendidas` |
| Documentación técnica de módulos | `08. Documentación Técnica del Proyecto` |

Si Confluence no está disponible, el skill confluence-publisher registrará el pendiente en `docs/CONFLUENCE_PENDING.md` — no hay nada adicional que hacer aquí.

## Lo que NO hacer

- No reescribir secciones de CLAUDE.md que siguen siendo precisas solo para "actualizar por actualizar"
- No crear un ADR por decisiones triviales o reversibles en minutos (elección de nombre de variable, orden de imports)
- No añadir entradas al CHANGELOG por cambios de documentación interna (ADRs y actualizaciones de CLAUDE.md no van al CHANGELOG)
- No bloquear el flujo de desarrollo esperando confirmación de publicación en Confluence
