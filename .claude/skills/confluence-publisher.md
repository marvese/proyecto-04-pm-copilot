# Skill: confluence-publisher

## Cuándo se activa

Tras crear o actualizar documentación significativa en el proyecto: nuevos ADRs, lecciones aprendidas, actualizaciones de prompts, documentación técnica de módulos o cualquier contenido que deba estar sincronizado en Confluence para que el equipo lo consulte.

También se invoca desde otros skills (docs-updater, prompt-librarian) como paso final de publicación.

## Mapa de documentos a páginas Confluence

Espacio: `PBPMIA` en `https://marvese.atlassian.net/wiki`

| Tipo de documento | Página Confluence destino |
|------------------|--------------------------|
| `docs/ADR-*.md` | `03. Arquitectura y Decisiones Técnicas` |
| Lecciones aprendidas / retrospectivas | `04. Lecciones Aprendidas` |
| `docs/PROMPTS.md` / nuevos prompts | `06. Biblioteca de Prompts` |
| Documentación técnica de módulos | `08. Documentación Técnica del Proyecto` |
| `docs/METODOLOGIA.md` | `01. Metodología PM con IA` |
| Diario / notas de sesión | `02. Diario de Desarrollo` |

## Proceso de publicación

### 1. Determinar la página destino

Leer el tipo de documento y consultar el mapa anterior. Si el tipo no tiene una página destino clara, preguntar al usuario antes de publicar.

### 2. Convertir Markdown a HTML de almacenamiento Confluence

Confluence almacena contenido en formato HTML de almacenamiento (`storage` representation). Convertir el Markdown del documento:

- Encabezados `#` → `<h1>`, `##` → `<h2>`, etc.
- Bloques de código ` ``` ` → `<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[...]]></ac:plain-text-body></ac:structured-macro>`
- Tablas Markdown → tablas HTML de Confluence
- Los enlaces internos (entre docs locales) se convierten en texto plano o se omiten

Para publicaciones simples, publicar el Markdown como contenido plano con la conversión básica es suficiente en MVP.

### 3. Llamar a la API REST de Confluence

#### Si la página ya existe: actualizar

```
PUT /wiki/rest/api/content/{pageId}
Authorization: Basic base64(email:api_token)
Content-Type: application/json

{
  "version": { "number": <current_version + 1> },
  "title": "<título de la página>",
  "type": "page",
  "body": {
    "storage": {
      "value": "<contenido HTML>",
      "representation": "storage"
    }
  }
}
```

#### Si es contenido nuevo dentro de una página existente: crear subpágina

```
POST /wiki/rest/api/content
{
  "type": "page",
  "title": "<título>",
  "space": { "key": "PBPMIA" },
  "ancestors": [{ "id": "<id de la página padre>" }],
  "body": { "storage": { "value": "...", "representation": "storage" } }
}
```

### 4. Verificar el resultado

- Si la respuesta HTTP es 200/201: registrar en el log que la publicación fue exitosa con el link a la página
- Si la respuesta es 4xx/5xx: pasar al manejo de fallo (ver §Manejo de fallos)

## Manejo de fallos — nunca bloquear el flujo

Si Confluence no está disponible (timeout, error 5xx, Circuit Breaker abierto, credenciales expiradas):

1. **No lanzar error al usuario** — continuar con el flujo de desarrollo
2. **Registrar el pendiente** en `docs/CONFLUENCE_PENDING.md`:

```markdown
## Pendientes de publicación en Confluence

| Fecha | Documento local | Página destino | Motivo del fallo |
|-------|----------------|----------------|-----------------|
| YYYY-MM-DD HH:MM | docs/ADR-006-xxx.md | 03. Arquitectura y Decisiones Técnicas | Connection timeout |
```

3. **Avisar al usuario** con un mensaje no bloqueante:
   > "No se pudo publicar en Confluence (timeout). Registrado en `docs/CONFLUENCE_PENDING.md` para publicar después."

### Reintento manual de pendientes

Cuando el usuario pida publicar los pendientes (o al inicio de sesión si hay pendientes), procesar `docs/CONFLUENCE_PENDING.md` y reintentar cada entrada. Si tiene éxito, eliminarla del fichero.

## Variables de entorno requeridas

Las credenciales vienen del `.env` via `python-dotenv`:

```
CONFLUENCE_BASE_URL=https://marvese.atlassian.net/wiki
CONFLUENCE_EMAIL=marvese@gmail.com
CONFLUENCE_API_TOKEN=...
CONFLUENCE_SPACE_KEY=PBPMIA
```

## Lo que NO hacer

- No bloquear el flujo de desarrollo si Confluence falla — los docs locales son la fuente de verdad
- No sobrescribir ediciones manuales hechas directamente en Confluence sin avisar al usuario
- No publicar datos sensibles (credenciales, API keys que puedan aparecer en logs de ejemplo)
- No crear páginas nuevas de primer nivel — solo actualizar las páginas del mapa o crear subpáginas dentro de ellas
