#!/usr/bin/env python3
"""fix_confluence_structure.py — Corrige la jerarquía de páginas en el espacio PBPMIA.

Problema detectado:
  - Las páginas 01, 02, 04, 05 son hijas del raíz del espacio en lugar de
    hijas de '00. PM Copilot — Inicio'.
  - Las páginas '03. Herramientas y Configuración' y
    '06. PM Copilot — Documentación Técnica' son obsoletas (títulos del
    primer script) y deben eliminarse.
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from confluence_client import ConfluenceClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PARENT_TITLE = "00. PM Copilot — Inicio"

PAGES_TO_MOVE = [
    "01. Metodología PM con IA",
    "02. Diario de Desarrollo",
    "04. Lecciones Aprendidas",
    "05. Playbook: Vibe Coding",
]

PAGES_TO_DELETE = [
    "03. Herramientas y Configuración",
    "06. PM Copilot — Documentación Técnica",
]


def main() -> None:
    client = ConfluenceClient.from_env()

    # ── Resolver el padre destino ─────────────────────────────────────────
    parent = client.get_page_by_title(PARENT_TITLE)
    if parent is None:
        sys.exit(f"Error: no se encontró la página padre '{PARENT_TITLE}'.")
    parent_id = parent["id"]
    print(f"Padre destino : '{PARENT_TITLE}' (id={parent_id})\n")

    moved, move_failed = [], []
    deleted, delete_failed = [], []

    # ── Mover páginas al padre correcto ───────────────────────────────────
    print("Moviendo páginas al padre correcto...")
    for title in PAGES_TO_MOVE:
        page = client.get_page_by_title(title)
        if page is None:
            print(f"  [!] '{title}' no encontrada — omitiendo.")
            move_failed.append(title)
            continue
        result = client.move_page(page["id"], parent_id)
        if result:
            print(f"  [→] '{title}' movida correctamente.")
            moved.append(title)
        else:
            print(f"  [✗] Error al mover '{title}'.")
            move_failed.append(title)

    # ── Eliminar páginas obsoletas ────────────────────────────────────────
    print("\nEliminando páginas obsoletas...")
    for title in PAGES_TO_DELETE:
        page = client.get_page_by_title(title)
        if page is None:
            print(f"  [!] '{title}' no encontrada — ya eliminada o nunca existió.")
            continue
        ok = client.delete_page(page["id"])
        if ok:
            print(f"  [✗] '{title}' eliminada.")
            deleted.append(title)
        else:
            print(f"  [!] Error al eliminar '{title}'.")
            delete_failed.append(title)

    # ── Resumen ───────────────────────────────────────────────────────────
    print(f"\n{'─' * 50}")
    print(f"  Páginas movidas:    {len(moved)}/{len(PAGES_TO_MOVE)}")
    print(f"  Páginas eliminadas: {len(deleted)}/{len(PAGES_TO_DELETE)}")
    if move_failed:
        print(f"  Fallos al mover:    {', '.join(move_failed)}")
    if delete_failed:
        print(f"  Fallos al eliminar: {', '.join(delete_failed)}")

    if move_failed or delete_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
