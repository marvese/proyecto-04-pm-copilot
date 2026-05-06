"""confluence_client.py — Cliente reutilizable para la API REST de Confluence.

Uso básico:
    from confluence_client import ConfluenceClient
    client = ConfluenceClient.from_env()
    page = client.publish_markdown("Mi página", markdown_text, parent_title="00. PM Copilot — Inicio")
"""
import json
import logging
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Convertidor Markdown → Confluence Storage Format
# ---------------------------------------------------------------------------

def _escape_cdata(text: str) -> str:
    return text.replace("]]>", "]]]]><![CDATA[>")


def _inline(text: str) -> str:
    """Formato inline: negrita, cursiva, código, enlaces.

    Los code spans se extraen primero con placeholders para que `*` dentro
    de backticks no sea capturado erróneamente por los regex de bold/italic.
    """
    # 1. Guardar code spans con placeholders para proteger su contenido
    code_spans: list[str] = []

    def _save_code(m: re.Match) -> str:  # type: ignore[type-arg]
        idx = len(code_spans)
        code_spans.append(f"<code>{m.group(1)}</code>")
        return f"\x00CODE{idx}\x00"

    text = re.sub(r"`([^`\n]+)`", _save_code, text)

    # 2. Aplicar bold/italic/enlaces sobre el texto sin code spans
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\n]+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    # 3. Restaurar code spans
    for i, span in enumerate(code_spans):
        text = text.replace(f"\x00CODE{i}\x00", span)

    return text


def markdown_to_storage(md: str) -> str:
    """Convierte Markdown a Confluence Storage Format (XHTML).

    Soporta: h1-h6, bloques de código con resaltado de sintaxis,
    tablas, listas, separadores y formato inline.
    """
    result: list[str] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    in_table = False
    table_rows: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        if list_items:
            inner = "\n".join(f"<li><p>{item}</p></li>" for item in list_items)
            result.append(f"<ul>\n{inner}\n</ul>")
            list_items.clear()

    def flush_table() -> None:
        nonlocal in_table
        if not table_rows:
            return
        parts = ["<table><tbody>"]
        header_done = False
        for row in table_rows:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if all(re.match(r"^[-: ]+$", c) for c in cells if c):
                continue  # fila separadora
            tag = "th" if not header_done else "td"
            parts.append(
                "<tr>" + "".join(f"<{tag}><p>{_inline(c)}</p></{tag}>" for c in cells) + "</tr>"
            )
            header_done = True
        parts.append("</tbody></table>")
        result.append("".join(parts))
        table_rows.clear()
        in_table = False

    for line in md.splitlines():
        # Bloques de código
        if line.startswith("```"):
            if in_code:
                content = _escape_cdata("\n".join(code_lines))
                lang_attr = (
                    f'<ac:parameter ac:name="language">{code_lang}</ac:parameter>'
                    if code_lang else ""
                )
                result.append(
                    f'<ac:structured-macro ac:name="code" ac:schema-version="1">'
                    f"{lang_attr}"
                    f"<ac:plain-text-body><![CDATA[{content}]]></ac:plain-text-body>"
                    f"</ac:structured-macro>"
                )
                in_code = False
                code_lang = ""
                code_lines.clear()
            else:
                flush_list()
                flush_table()
                in_code = True
                code_lang = line[3:].strip()
            continue

        if in_code:
            code_lines.append(line)
            continue

        # Tablas
        if line.strip().startswith("|") and "|" in line:
            flush_list()
            in_table = True
            table_rows.append(line)
            continue
        if in_table:
            flush_table()

        # Encabezados
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush_list()
            lvl = len(m.group(1))
            result.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            continue

        # Separadores horizontales
        if re.match(r"^[-*_]{3,}\s*$", line):
            flush_list()
            result.append("<hr/>")
            continue

        # Listas
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            list_items.append(_inline(m.group(1)))
            continue

        # Línea vacía
        if not line.strip():
            flush_list()
            result.append("")
            continue

        # Párrafo normal
        result.append(f"<p>{_inline(line)}</p>")

    flush_list()
    flush_table()
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Cliente Confluence
# ---------------------------------------------------------------------------

class ConfluenceClient:
    """Cliente para la API REST de Confluence v2 (Cloud).

    Todos los métodos retornan el objeto JSON de la página en éxito,
    o None en caso de error (el error queda logueado).
    """

    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        space_key: str,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.space_key = space_key
        self._auth = (email, api_token)
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ------------------------------------------------------------------
    # Constructor desde variables de entorno
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "ConfluenceClient":
        """Crea un cliente con las credenciales del .env."""
        base_url = (
            os.getenv("CONFLUENCE_BASE_URL")
            or (os.getenv("CONFLUENCE_URL", "").rstrip("/") + "/wiki")
        )
        email = os.getenv("CONFLUENCE_EMAIL", "")
        token = os.getenv("CONFLUENCE_API_TOKEN", "")
        space = os.getenv("CONFLUENCE_SPACE_KEY", "")

        missing = [k for k, v in [
            ("CONFLUENCE_BASE_URL", base_url),
            ("CONFLUENCE_EMAIL", email),
            ("CONFLUENCE_API_TOKEN", token),
            ("CONFLUENCE_SPACE_KEY", space),
        ] if not v]
        if missing:
            raise EnvironmentError(
                f"Faltan variables de entorno: {', '.join(missing)}"
            )

        return cls(base_url, email, token, space)

    # ------------------------------------------------------------------
    # Capa de transporte
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> dict | None:
        """Ejecuta una llamada HTTP a la API. Retorna JSON o None en caso de error."""
        url = f"{self.base_url}/rest/api/{path.lstrip('/')}"
        try:
            resp = requests.request(
                method,
                url,
                auth=self._auth,
                headers=self._headers,
                timeout=30,
                **kwargs,
            )
        except requests.exceptions.Timeout:
            logger.error("Timeout al conectar con Confluence (%s %s)", method, url)
            return None
        except requests.exceptions.ConnectionError as exc:
            logger.error("Error de conexión con Confluence: %s", exc)
            return None

        if not resp.ok:
            try:
                detail = resp.json().get("message", resp.text[:300])
            except Exception:
                detail = resp.text[:300]
            logger.error(
                "Confluence API %d en %s %s — %s",
                resp.status_code,
                method,
                url,
                detail,
            )
            return None

        return resp.json()

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def get_page_by_title(self, title: str) -> dict | None:
        """Busca una página por título en el espacio configurado.

        Retorna el objeto de la página con campos `id`, `version` y `title`,
        o None si no existe o la llamada falla.
        """
        data = self._request(
            "GET",
            "content",
            params={
                "spaceKey": self.space_key,
                "title": title,
                "type": "page",
                "expand": "version",
            },
        )
        if data is None:
            return None
        results = data.get("results", [])
        if not results:
            logger.debug("Página '%s' no encontrada en el espacio %s.", title, self.space_key)
            return None
        return results[0]

    def create_page(
        self,
        title: str,
        content: str,
        parent_title: str,
    ) -> dict | None:
        """Crea una página nueva como hija de `parent_title`.

        `content` debe estar en Confluence Storage Format (XHTML).
        Retorna el objeto de la página creada o None en caso de error.
        """
        parent = self.get_page_by_title(parent_title)
        if parent is None:
            logger.error(
                "No se puede crear '%s': página padre '%s' no encontrada.",
                title,
                parent_title,
            )
            return None

        logger.info("Creando página '%s' bajo '%s'...", title, parent_title)
        return self._request(
            "POST",
            "content",
            data=json.dumps({
                "type": "page",
                "title": title,
                "space": {"key": self.space_key},
                "ancestors": [{"id": parent["id"]}],
                "body": {"storage": {"value": content, "representation": "storage"}},
            }),
        )

    def update_page(
        self,
        page_id: str,
        title: str,
        content: str,
        version: int,
    ) -> dict | None:
        """Actualiza el contenido de una página existente.

        `version` debe ser el número de versión actual (se incrementa en 1 automáticamente).
        `content` debe estar en Confluence Storage Format (XHTML).
        Retorna el objeto actualizado o None en caso de error.
        """
        logger.info("Actualizando página '%s' (v%d → v%d)...", title, version, version + 1)
        return self._request(
            "PUT",
            f"content/{page_id}",
            data=json.dumps({
                "type": "page",
                "title": title,
                "version": {"number": version + 1},
                "body": {"storage": {"value": content, "representation": "storage"}},
            }),
        )

    def move_page(self, page_id: str, new_parent_id: str) -> dict | None:
        """Mueve una página a un nuevo padre conservando su contenido.

        Obtiene el cuerpo actual de la página antes de hacer el PUT para no
        perder el contenido (la API requiere el body en cada PUT).
        """
        current = self._request(
            "GET",
            f"content/{page_id}",
            params={"expand": "version,body.storage"},
        )
        if current is None:
            return None

        logger.info(
            "Moviendo '%s' (id=%s) a nuevo padre id=%s...",
            current["title"],
            page_id,
            new_parent_id,
        )
        return self._request(
            "PUT",
            f"content/{page_id}",
            data=json.dumps({
                "type": "page",
                "title": current["title"],
                "version": {"number": current["version"]["number"] + 1},
                "ancestors": [{"id": new_parent_id}],
                "body": {
                    "storage": {
                        "value": current["body"]["storage"]["value"],
                        "representation": "storage",
                    }
                },
            }),
        )

    def delete_page(self, page_id: str) -> bool:
        """Elimina una página permanentemente. Retorna True si tuvo éxito."""
        url = f"{self.base_url}/rest/api/content/{page_id}"
        try:
            resp = requests.delete(url, auth=self._auth, headers=self._headers, timeout=30)
        except requests.exceptions.RequestException as exc:
            logger.error("Error de red al eliminar página %s: %s", page_id, exc)
            return False

        if resp.status_code == 204:
            logger.info("Página %s eliminada.", page_id)
            return True

        try:
            detail = resp.json().get("message", resp.text[:300])
        except Exception:
            detail = resp.text[:300]
        logger.error("Error %d al eliminar página %s — %s", resp.status_code, page_id, detail)
        return False

    def publish_markdown(
        self,
        title: str,
        markdown_content: str,
        parent_title: str,
    ) -> dict | None:
        """Convierte `markdown_content` a Storage Format y publica la página.

        Si la página ya existe la actualiza; si no existe la crea bajo `parent_title`.
        Retorna el objeto de la página publicada o None en caso de error.
        """
        storage = markdown_to_storage(markdown_content)
        existing = self.get_page_by_title(title)

        if existing:
            return self.update_page(
                existing["id"],
                title,
                storage,
                existing["version"]["number"],
            )
        return self.create_page(title, storage, parent_title)
