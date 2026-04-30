#!/usr/bin/env python3
"""publish_tech_docs.py — Publica INSTALL.md y RUNBOOK.md en Confluence.

Páginas destino (hijas de '08. Documentación Técnica del Proyecto'):
  - Guía de Instalación
  - Runbook — Operaciones del día a día

Uso:
    python3 scripts/publish_tech_docs.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from confluence_client import ConfluenceClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

ROOT = Path(__file__).parent.parent
PARENT_PAGE = "08. Documentación Técnica del Proyecto"

DOCS = [
    ("Guía de Instalación", ROOT / "docs" / "INSTALL.md"),
    ("Runbook — Operaciones del día a día", ROOT / "docs" / "RUNBOOK.md"),
]


def main() -> None:
    try:
        client = ConfluenceClient.from_env()
    except EnvironmentError as exc:
        sys.exit(f"Error de configuración: {exc}")

    for title, path in DOCS:
        if not path.exists():
            print(f"✗ No se encontró {path} — omitiendo")
            continue

        content = path.read_text(encoding="utf-8")
        print(f"Publicando '{title}' ({path.name}, {len(content)} chars)...")

        page = client.publish_markdown(title, content, PARENT_PAGE)
        if page is None:
            print(f"✗ Error publicando '{title}'. Revisa los logs.")
            continue

        web_ui = page.get("_links", {}).get("webui", "")
        url = f"{client.base_url}{web_ui}" if web_ui else f"id={page.get('id', '?')}"
        print(f"✓ '{title}' → {url}")


if __name__ == "__main__":
    main()
