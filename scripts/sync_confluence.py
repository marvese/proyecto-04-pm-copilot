#!/usr/bin/env python3
"""sync_confluence.py — Sincroniza ficheros .md locales con páginas de Confluence.

Modos de uso
------------
Fichero individual:
    python3 scripts/sync_confluence.py docs/CHANGELOG.md
    python3 scripts/sync_confluence.py docs/ARCHITECTURE.md \\
        --parent "08. Documentación Técnica del Proyecto"
    python3 scripts/sync_confluence.py docs/INSTALL.md --title "Guía de instalación"

Batch (sin argumentos): procesa todos los .md de docs/pending/confluence/
    python3 scripts/sync_confluence.py
    python3 scripts/sync_confluence.py --dry-run

Frontmatter (solo para modo batch):
    Los ficheros en docs/pending/confluence/ pueden incluir una cabecera YAML
    opcional que indica el padre y el título en Confluence:

        ---
        parent: "08. Documentación Técnica del Proyecto"
        title: "ARCHITECTURE v0.3"
        ---
        # Resto del contenido...

    Sin frontmatter se usa el nombre del fichero como título y solo se
    actualiza si la página ya existe (sin padre no se puede crear).

Variables de entorno requeridas (.env en la raíz del proyecto):
    CONFLUENCE_BASE_URL  o  CONFLUENCE_URL
    CONFLUENCE_EMAIL
    CONFLUENCE_API_TOKEN
    CONFLUENCE_SPACE_KEY
"""
from __future__ import annotations

import argparse
import logging
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from confluence_client import ConfluenceClient, markdown_to_storage  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

ROOT = Path(__file__).parent.parent
PENDING_DIR = ROOT / "docs" / "pending" / "confluence"
PUBLISHED_DIR = ROOT / "docs" / "published"

# ─── frontmatter ─────────────────────────────────────────────────────────────

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_KV_RE = re.compile(r'^(\w+)\s*:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Extrae el bloque YAML frontmatter (si existe) y devuelve (meta, body)."""
    m = _FM_RE.match(content)
    if not m:
        return {}, content
    meta = dict(_KV_RE.findall(m.group(1)))
    body = content[m.end():]
    return meta, body


# ─── sync de un único fichero ─────────────────────────────────────────────────

def sync_file(
    md_path: Path,
    client: ConfluenceClient,
    parent_override: str | None = None,
    title_override: str | None = None,
    dry_run: bool = False,
) -> bool:
    """Sube md_path a Confluence. Retorna True si tuvo éxito."""
    raw_content = md_path.read_text(encoding="utf-8")
    meta, content = parse_frontmatter(raw_content)

    page_title = title_override or meta.get("title") or md_path.stem
    parent = parent_override or meta.get("parent")

    relative = md_path.relative_to(ROOT) if md_path.is_relative_to(ROOT) else md_path
    size_kb = len(content.encode()) // 1024 or 1

    print(f"\nFichero  : {relative} ({size_kb} KB)")
    print(f"Título   : {page_title}")
    print(f"Padre    : {parent or '(se infiere si la página ya existe)'}")

    if dry_run:
        print("[dry-run] Omitido.")
        return True

    existing = client.get_page_by_title(page_title)

    if existing:
        print(f"Acción   : ACTUALIZAR (id={existing['id']}, v{existing['version']['number']})")
        storage = markdown_to_storage(content)
        result = client.update_page(
            existing["id"],
            page_title,
            storage,
            existing["version"]["number"],
        )
    else:
        if not parent:
            print(
                "ADVERTENCIA: la página no existe y no se especificó padre — omitido.\n"
                "  Añade 'parent: \"Título padre\"' al frontmatter del fichero."
            )
            return False
        print(f"Acción   : CREAR bajo '{parent}'")
        result = client.publish_markdown(page_title, content, parent)

    if result is None:
        print("ERROR: no se pudo sincronizar. Revisa los logs.")
        return False

    web_ui = result.get("_links", {}).get("webui", "")
    url = f"{client.base_url}{web_ui}" if web_ui else f"id={result.get('id', '?')}"
    print(f"✓ Sincronizado → {url}")
    return True


# ─── modo batch ───────────────────────────────────────────────────────────────

def run_batch(client: ConfluenceClient, dry_run: bool) -> None:
    """Procesa todos los .md de docs/pending/confluence/."""
    pending = sorted(PENDING_DIR.glob("*.md"))
    if not pending:
        print("No hay ficheros pendientes en docs/pending/confluence/")
        return

    print(f"Procesando {len(pending)} fichero(s) en modo batch…")
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    ok = fail = skip = 0
    today = date.today().isoformat()

    for md_path in pending:
        success = sync_file(md_path, client, dry_run=dry_run)
        if success:
            ok += 1
            if not dry_run:
                dest = PUBLISHED_DIR / f"{today}_{md_path.name}"
                shutil.move(str(md_path), dest)
                print(f"  → movido a docs/published/{dest.name}")
        else:
            # Ficheros sin padre configurado quedan en pending para revisión
            skip += 1

    print(f"\nResumen: {ok} OK · {fail} error · {skip} omitido(s)")


# ─── modo individual ─────────────────────────────────────────────────────────

def resolve_path(raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    candidate = ROOT / p
    if candidate.exists():
        return candidate
    return Path.cwd() / p


def run_single(args: argparse.Namespace, client: ConfluenceClient) -> None:
    md_path = resolve_path(args.file)
    if not md_path.exists():
        sys.exit(f"Error: no se encontró el fichero '{md_path}'")
    if md_path.suffix.lower() != ".md":
        sys.exit(f"Error: se esperaba un fichero .md, recibido '{md_path.name}'")

    success = sync_file(
        md_path,
        client,
        parent_override=args.parent,
        title_override=args.title,
        dry_run=args.dry_run,
    )
    if not success:
        sys.exit(1)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sincroniza ficheros .md con Confluence.\n"
            "Sin argumentos: modo batch — procesa docs/pending/confluence/*.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        metavar="FILE.md",
        nargs="?",
        default=None,
        help="Fichero Markdown a subir. Omitir para modo batch.",
    )
    parser.add_argument(
        "--parent",
        metavar="TÍTULO",
        default=None,
        help="Página padre en Confluence (solo modo individual).",
    )
    parser.add_argument(
        "--title",
        metavar="TÍTULO",
        default=None,
        help="Título de la página (por defecto: nombre del fichero).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra qué haría sin realizar ninguna llamada a la API.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.dry_run and not args.file:
        print("[dry-run] Modo batch — simulación sin llamadas a la API.")

    try:
        client = ConfluenceClient.from_env()
    except EnvironmentError as exc:
        sys.exit(f"Error de configuración: {exc}")

    print(f"Espacio  : {client.space_key}")

    if args.file is None:
        run_batch(client, args.dry_run)
    else:
        run_single(args, client)


if __name__ == "__main__":
    main()
