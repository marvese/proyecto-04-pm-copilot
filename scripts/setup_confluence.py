#!/usr/bin/env python3
"""setup_confluence.py — Crea/actualiza la estructura de páginas PM Copilot en Confluence.

Idempotente: si una página ya existe la actualiza sin duplicar.
Publica docs/PROMPTS.md en la página '06. Biblioteca de Prompts'.
"""
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

BASE_URL = (
    os.getenv("CONFLUENCE_BASE_URL")
    or (os.getenv("CONFLUENCE_URL", "").rstrip("/") + "/wiki")
).rstrip("/")
EMAIL = os.getenv("CONFLUENCE_EMAIL", "")
API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "")
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "")

AUTH = (EMAIL, API_TOKEN)
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def _validate_config() -> None:
    missing = [
        name
        for name, val in [
            ("CONFLUENCE_BASE_URL o CONFLUENCE_URL", BASE_URL),
            ("CONFLUENCE_EMAIL", EMAIL),
            ("CONFLUENCE_API_TOKEN", API_TOKEN),
            ("CONFLUENCE_SPACE_KEY", SPACE_KEY),
        ]
        if not val
    ]
    if missing:
        sys.exit(f"Error: faltan variables de entorno: {', '.join(missing)}")


# ---------------------------------------------------------------------------
# Convertidor Markdown → Confluence Storage Format
# ---------------------------------------------------------------------------

def _escape_cdata(text: str) -> str:
    """Escapa ']]>' dentro de bloques CDATA."""
    return text.replace("]]>", "]]]]><![CDATA[>")


def _inline(text: str) -> str:
    """Convierte formato inline de Markdown a HTML."""
    # Negrita antes que cursiva para no confundir **bold* con cursiva
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\n]+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_storage(md: str) -> str:
    """
    Convierte Markdown a Confluence Storage Format (XHTML).
    Soporta: encabezados h1-h6, bloques de código, tablas, listas y párrafos.
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
            inner = "\n".join(f"<li>{item}</li>" for item in list_items)
            result.append(f"<ul>\n{inner}\n</ul>")
            list_items.clear()

    def flush_table() -> None:
        nonlocal in_table
        if not table_rows:
            return
        html_parts = ["<table><tbody>"]
        header_emitted = False
        for row in table_rows:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            # Omitir fila separadora (---|---|---)
            if all(re.match(r"^[-: ]+$", c) for c in cells if c):
                continue
            tag = "th" if not header_emitted else "td"
            html_parts.append(
                "<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>"
            )
            header_emitted = True
        html_parts.append("</tbody></table>")
        result.append("".join(html_parts))
        table_rows.clear()
        in_table = False

    for line in md.splitlines():
        # ── Bloques de código ──────────────────────────────────────────────
        if line.startswith("```"):
            if in_code:
                content = _escape_cdata("\n".join(code_lines))
                lang_attr = (
                    f'<ac:parameter ac:name="language">{code_lang}</ac:parameter>'
                    if code_lang
                    else ""
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

        # ── Tablas ────────────────────────────────────────────────────────
        if line.strip().startswith("|") and "|" in line:
            flush_list()
            in_table = True
            table_rows.append(line)
            continue
        if in_table:
            flush_table()

        # ── Encabezados ───────────────────────────────────────────────────
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush_list()
            lvl = len(m.group(1))
            result.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            continue

        # ── Separadores horizontales ──────────────────────────────────────
        if re.match(r"^[-*_]{3,}\s*$", line):
            flush_list()
            result.append("<hr/>")
            continue

        # ── Listas (- o *) ────────────────────────────────────────────────
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            list_items.append(_inline(m.group(1)))
            continue

        # ── Línea vacía ───────────────────────────────────────────────────
        if not line.strip():
            flush_list()
            result.append("")
            continue

        # ── Párrafo normal ────────────────────────────────────────────────
        result.append(f"<p>{_inline(line)}</p>")

    # Volcar buffers pendientes al final
    flush_list()
    flush_table()

    return "\n".join(result)


# ---------------------------------------------------------------------------
# API de Confluence
# ---------------------------------------------------------------------------

def _api(method: str, path: str, **kwargs) -> dict:
    """Wrapper HTTP con manejo de errores descriptivo."""
    url = f"{BASE_URL}/rest/api/{path.lstrip('/')}"
    resp = requests.request(method, url, auth=AUTH, headers=HEADERS, **kwargs)
    if not resp.ok:
        print(f"\n  [!] Error {resp.status_code} en {method} {url}")
        try:
            detail = resp.json()
            print(f"      {detail.get('message', resp.text[:200])}")
        except Exception:
            print(f"      {resp.text[:200]}")
        resp.raise_for_status()
    return resp.json()


def get_root_page() -> dict:
    """Retorna la página raíz del espacio (la que no tiene ancestros)."""
    data = _api(
        "GET",
        "content",
        params={"spaceKey": SPACE_KEY, "type": "page", "expand": "ancestors", "limit": 50},
    )
    roots = [p for p in data.get("results", []) if not p.get("ancestors")]
    if not roots:
        sys.exit(f"No se encontró página raíz en el espacio {SPACE_KEY}.")
    return roots[0]


def find_page(title: str) -> dict | None:
    """Busca una página por título en el espacio. Retorna el objeto o None."""
    data = _api(
        "GET",
        "content",
        params={
            "spaceKey": SPACE_KEY,
            "title": title,
            "type": "page",
            "expand": "version",
        },
    )
    results = data.get("results", [])
    return results[0] if results else None


def create_page(parent_id: str, title: str, body_html: str) -> dict:
    return _api(
        "POST",
        "content",
        data=json.dumps({
            "type": "page",
            "title": title,
            "space": {"key": SPACE_KEY},
            "ancestors": [{"id": parent_id}],
            "body": {"storage": {"value": body_html, "representation": "storage"}},
        }),
    )


def update_page(page_id: str, title: str, body_html: str, version: int) -> dict:
    return _api(
        "PUT",
        f"content/{page_id}",
        data=json.dumps({
            "type": "page",
            "title": title,
            "version": {"number": version + 1},
            "body": {"storage": {"value": body_html, "representation": "storage"}},
        }),
    )


def upsert_page(parent_id: str, title: str, body_html: str) -> tuple[dict, str]:
    """Crea la página si no existe; la actualiza si existe. Retorna (page, acción)."""
    existing = find_page(title)
    if existing:
        page = update_page(
            existing["id"], title, body_html, existing["version"]["number"]
        )
        return page, "updated"
    page = create_page(parent_id, title, body_html)
    return page, "created"


# ---------------------------------------------------------------------------
# Contenido de las páginas
# ---------------------------------------------------------------------------

_PLACEHOLDER = "<p><em>Contenido pendiente de publicación.</em></p>"


def _load_prompts_as_storage() -> str:
    path = ROOT_DIR / "docs" / "PROMPTS.md"
    if not path.exists():
        print("  [!] docs/PROMPTS.md no encontrado — usando placeholder.")
        return _PLACEHOLDER
    print(f"  Convirtiendo docs/PROMPTS.md ({path.stat().st_size // 1024} KB)...")
    return markdown_to_storage(path.read_text(encoding="utf-8"))


def _page_structure() -> dict:
    """Define la jerarquía completa de páginas con su contenido."""
    return {
        "title": "00. PM Copilot — Inicio",
        "body": (
            "<p>Bienvenido a la documentación de <strong>PM Copilot</strong>: "
            "un asistente inteligente con RAG para la gestión de proyectos de software.</p>"
            "<p>Navega por las secciones del menú lateral para explorar la metodología, "
            "arquitectura, decisiones técnicas y recursos del proyecto.</p>"
        ),
        "children": [
            {
                "title": "01. Metodología PM con IA",
                "body": (
                    "<p>Metodología de gestión de proyectos adaptada al desarrollo con "
                    "inteligencia artificial: sprints de una semana, user stories para LLMs "
                    "y criterios de aceptación para comportamientos no deterministas.</p>"
                    "<p>Ver <code>docs/METODOLOGIA.md</code> en el repositorio para la "
                    "especificación completa.</p>"
                ),
            },
            {
                "title": "02. Diario de Desarrollo",
                "body": (
                    "<p>Registro cronológico del proceso de desarrollo: decisiones tomadas, "
                    "experimentos realizados y aprendizajes obtenidos sesión a sesión.</p>"
                ),
            },
            {
                "title": "03. Arquitectura y Decisiones Técnicas",
                "body": (
                    "<p>Arquitectura hexagonal del sistema y registro de decisiones de "
                    "arquitectura (ADRs). Los ADRs completos están disponibles en el "
                    "repositorio bajo <code>docs/ADR-*.md</code>.</p>"
                    "<ul>"
                    "<li>ADR-001: Stack tecnológico</li>"
                    "<li>ADR-002: Arquitectura hexagonal vs microservicios</li>"
                    "<li>ADR-003: Circuit Breaker en integraciones externas</li>"
                    "<li>ADR-004: PWA React primero, Flutter POC después</li>"
                    "<li>ADR-005: LLM Router y embeddings RAG</li>"
                    "</ul>"
                ),
            },
            {
                "title": "04. Lecciones Aprendidas",
                "body": (
                    "<p>Compilación de lecciones aprendidas, errores cometidos y buenas "
                    "prácticas identificadas a lo largo del proyecto. "
                    "Actualizado al final de cada sprint.</p>"
                ),
            },
            {
                "title": "05. Playbook: Vibe Coding",
                "body": (
                    "<p>Guía práctica del enfoque Vibe Coding aplicado a este proyecto: "
                    "flujos de trabajo, prompts efectivos y patrones reutilizables para "
                    "desarrollo asistido por IA.</p>"
                ),
            },
            {
                "title": "06. Biblioteca de Prompts",
                "body": _load_prompts_as_storage(),
            },
            {
                "title": "07. Herramientas y Configuración",
                "body": (
                    "<p>Documentación de las herramientas utilizadas, su configuración "
                    "y la integración entre ellas en el ecosistema del proyecto: "
                    "Ollama, ChromaDB, Railway, Vercel, Confluence, Jira y GitHub.</p>"
                ),
            },
            {
                "title": "08. Documentación Técnica del Proyecto",
                "body": (
                    "<p>Documentación técnica del sistema PM Copilot: arquitectura de "
                    "adaptadores hexagonales, contratos de API REST/WebSocket, "
                    "modelos de datos y guías de despliegue.</p>"
                ),
            },
        ],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _validate_config()
    print(f"Conectando a {BASE_URL} — espacio {SPACE_KEY}\n")

    root = get_root_page()
    print(f"Raíz del espacio : '{root['title']}' (id={root['id']})\n")

    structure = _page_structure()
    summary: list[dict] = []

    # Crear/actualizar la página raíz del proyecto (00.)
    print(f"Procesando '{structure['title']}'...")
    page_00, action_00 = upsert_page(root["id"], structure["title"], structure["body"])
    parent_id = page_00["id"]
    summary.append({"title": structure["title"], "action": action_00, "id": parent_id})
    _print_result(structure["title"], action_00, parent_id)

    # Crear/actualizar las subpáginas (01.–08.)
    print()
    for child in structure["children"]:
        page, action = upsert_page(parent_id, child["title"], child["body"])
        summary.append({"title": child["title"], "action": action, "id": page["id"]})
        _print_result(child["title"], action, page["id"])

    # Resumen final
    _print_summary(summary)


def _print_result(title: str, action: str, page_id: str) -> None:
    icon = "✓" if action == "updated" else "+"
    print(f"  [{icon}] {title} ({action}, id={page_id})")


def _print_summary(summary: list[dict]) -> None:
    created = [s for s in summary if s["action"] == "created"]
    updated = [s for s in summary if s["action"] == "updated"]

    print(f"\n{'─' * 52}")
    print(f"  Páginas creadas:      {len(created)}")
    print(f"  Páginas actualizadas: {len(updated)}")
    print(f"  Total procesadas:     {len(summary)}")

    if created:
        print(f"\n  Nuevas:")
        for s in created:
            print(f"    +  {s['title']}")
    if updated:
        print(f"\n  Actualizadas:")
        for s in updated:
            print(f"    ✓  {s['title']}")

    print(f"\n  Espacio: {BASE_URL}/spaces/{SPACE_KEY}\n")


if __name__ == "__main__":
    main()
