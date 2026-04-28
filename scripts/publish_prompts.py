#!/usr/bin/env python3
"""publish_prompts.py — Publica docs/PROMPTS.md en la página '06. Biblioteca de Prompts'.

Uso:
    python3 scripts/publish_prompts.py
"""
import logging
import sys
from pathlib import Path

# Permite importar confluence_client.py desde el mismo directorio
sys.path.insert(0, str(Path(__file__).parent))
from confluence_client import ConfluenceClient

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

ROOT = Path(__file__).parent.parent
PROMPTS_FILE = ROOT / "docs" / "PROMPTS.md"
TARGET_PAGE = "06. Biblioteca de Prompts"
PARENT_PAGE = "00. PM Copilot — Inicio"


def main() -> None:
    if not PROMPTS_FILE.exists():
        sys.exit(f"Error: no se encontró {PROMPTS_FILE}")

    size_kb = PROMPTS_FILE.stat().st_size // 1024
    print(f"Leyendo {PROMPTS_FILE.relative_to(ROOT)} ({size_kb} KB)...")

    content = PROMPTS_FILE.read_text(encoding="utf-8")

    try:
        client = ConfluenceClient.from_env()
    except EnvironmentError as exc:
        sys.exit(f"Error de configuración: {exc}")

    print(f"Publicando en '{TARGET_PAGE}' (espacio {client.space_key})...")
    page = client.publish_markdown(TARGET_PAGE, content, PARENT_PAGE)

    if page is None:
        sys.exit("No se pudo publicar. Revisa los logs para más detalles.")

    page_id = page.get("id", "?")
    web_ui = page.get("_links", {}).get("webui", "")
    full_url = f"{client.base_url}{web_ui}" if web_ui else f"id={page_id}"

    print(f"✓ Publicado correctamente → {full_url}")


if __name__ == "__main__":
    main()
