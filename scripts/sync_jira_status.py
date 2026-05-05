#!/usr/bin/env python3
"""sync_jira_status.py — Actualiza el estado de tareas Jira desde un fichero JSON.

Lee docs/pending/jira/update-tasks.json con el formato:
    [
      {"key": "PMCP-52", "status": "Done", "comment": "Implementado y testeado."},
      {"key": "PMCP-48", "status": "In Progress"}
    ]

Campos por entrada:
    key      (obligatorio) — clave del issue Jira, ej. "PMCP-52"
    status   (obligatorio) — nombre del estado destino (case-insensitive)
                            Valores habituales: "Done", "In Progress", "To Do"
    comment  (opcional)   — comentario que se añade al issue tras la transición

Tras procesar con éxito, el fichero se mueve a:
    docs/published/YYYY-MM-DD_update-tasks.json

Variables de entorno requeridas (.env en la raíz del proyecto):
    JIRA_URL
    JIRA_EMAIL
    JIRA_API_TOKEN

Uso:
    python3 scripts/sync_jira_status.py
    python3 scripts/sync_jira_status.py --dry-run
    python3 scripts/sync_jira_status.py --file docs/pending/jira/update-tasks.json
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

ROOT = Path(__file__).parent.parent
DEFAULT_PENDING = ROOT / "docs" / "pending" / "jira" / "update-tasks.json"
PUBLISHED_DIR = ROOT / "docs" / "published"

# ─── Jira client ─────────────────────────────────────────────────────────────

class JiraClient:
    def __init__(self, base_url: str, email: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._auth = (email, token)
        self._headers = {"Content-Type": "application/json", "Accept": "application/json"}

    @classmethod
    def from_env(cls) -> "JiraClient":
        url = os.getenv("JIRA_URL", "")
        email = os.getenv("JIRA_EMAIL", "")
        token = os.getenv("JIRA_API_TOKEN", "")
        missing = [k for k, v in [("JIRA_URL", url), ("JIRA_EMAIL", email), ("JIRA_API_TOKEN", token)] if not v]
        if missing:
            raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing)}")
        return cls(url, email, token)

    def _get(self, path: str, **params) -> dict | list | None:
        url = f"{self.base_url}/rest/api/3/{path.lstrip('/')}"
        try:
            resp = requests.get(url, auth=self._auth, headers=self._headers, params=params, timeout=30)
        except requests.exceptions.RequestException as exc:
            logging.error("Error de red: %s", exc)
            return None
        if not resp.ok:
            logging.error("GET %s → %d: %s", path, resp.status_code, resp.text[:200])
            return None
        return resp.json()

    def _post(self, path: str, body: dict) -> bool:
        url = f"{self.base_url}/rest/api/3/{path.lstrip('/')}"
        try:
            resp = requests.post(
                url, auth=self._auth, headers=self._headers,
                json=body, timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            logging.error("Error de red: %s", exc)
            return False
        if resp.status_code not in (200, 201, 204):
            logging.error("POST %s → %d: %s", path, resp.status_code, resp.text[:200])
            return False
        return True

    def get_transitions(self, issue_key: str) -> list[dict]:
        data = self._get(f"issue/{issue_key}/transitions")
        return (data or {}).get("transitions", [])

    def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        return self._post(
            f"issue/{issue_key}/transitions",
            {"transition": {"id": transition_id}},
        )

    def add_comment(self, issue_key: str, text: str) -> bool:
        return self._post(
            f"issue/{issue_key}/comment",
            {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": text}],
                        }
                    ],
                }
            },
        )


# ─── procesar una entrada ─────────────────────────────────────────────────────

def process_entry(entry: dict, client: JiraClient, dry_run: bool) -> bool:
    key = entry.get("key", "").strip()
    target_status = entry.get("status", "").strip()
    comment = entry.get("comment", "").strip()

    if not key or not target_status:
        print(f"  SKIP: entrada incompleta — {entry}")
        return False

    print(f"\n  {key} → '{target_status}'")

    transitions = client.get_transitions(key)
    if not transitions:
        print(f"  ERROR: no se pudieron obtener transiciones para {key}")
        return False

    match = next(
        (t for t in transitions if t["name"].lower() == target_status.lower()),
        None,
    )
    if match is None:
        available = [t["name"] for t in transitions]
        print(f"  ERROR: transición '{target_status}' no disponible. Disponibles: {available}")
        return False

    if dry_run:
        print(f"  [dry-run] Transición id={match['id']} nombre='{match['name']}'")
        if comment:
            print(f"  [dry-run] Comentario: {comment[:80]}{'...' if len(comment) > 80 else ''}")
        return True

    ok = client.transition_issue(key, match["id"])
    if not ok:
        print(f"  ERROR: falló la transición de {key}")
        return False

    print(f"  ✓ Estado actualizado a '{match['name']}'")

    if comment:
        if client.add_comment(key, comment):
            print(f"  ✓ Comentario añadido")
        else:
            print(f"  ADVERTENCIA: transición OK pero falló al añadir comentario")

    return True


# ─── main ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Actualiza el estado de tareas Jira desde docs/pending/jira/update-tasks.json"
    )
    parser.add_argument(
        "--file",
        metavar="PATH",
        default=str(DEFAULT_PENDING),
        help=f"Fichero JSON de tareas a actualizar (default: {DEFAULT_PENDING.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra qué haría sin realizar ninguna llamada a Jira.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.file)
    if not input_path.is_absolute():
        input_path = ROOT / input_path

    if not input_path.exists():
        sys.exit(
            f"No se encontró el fichero de tareas: {input_path}\n"
            f"Crea docs/pending/jira/update-tasks.json con el formato:\n"
            f'[{{"key": "PMCP-52", "status": "Done", "comment": "Opcional"}}]'
        )

    try:
        tasks = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"Error al parsear {input_path.name}: {exc}")

    if not isinstance(tasks, list) or not tasks:
        sys.exit("El fichero debe contener una lista JSON no vacía.")

    print(f"Fichero  : {input_path.relative_to(ROOT)}")
    print(f"Tareas   : {len(tasks)}")
    if args.dry_run:
        print("[dry-run] No se realizarán cambios en Jira.")

    try:
        client = JiraClient.from_env()
    except EnvironmentError as exc:
        sys.exit(f"Error de configuración: {exc}")

    ok = fail = 0
    for entry in tasks:
        if process_entry(entry, client, args.dry_run):
            ok += 1
        else:
            fail += 1

    print(f"\nResumen: {ok} OK · {fail} error(s)")

    if not args.dry_run and fail == 0:
        PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
        today = date.today().isoformat()
        dest = PUBLISHED_DIR / f"{today}_{input_path.name}"
        # Si ya existe un archivo con ese nombre en published, añadir sufijo
        if dest.exists():
            stem = input_path.stem
            suffix = input_path.suffix
            i = 1
            while dest.exists():
                dest = PUBLISHED_DIR / f"{today}_{stem}_{i}{suffix}"
                i += 1
        shutil.move(str(input_path), dest)
        print(f"→ movido a docs/published/{dest.name}")
    elif not args.dry_run and fail > 0:
        print(f"ADVERTENCIA: {fail} tarea(s) fallaron — el fichero no se mueve para poder reintentarlo.")


if __name__ == "__main__":
    main()
