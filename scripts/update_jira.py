"""update_jira.py — Actualiza descripción y story points en Jira desde jira_descriptions_complete.json.

Uso:
    python3 scripts/update_jira.py
    python3 scripts/update_jira.py --dry-run   # muestra lo que haría sin ejecutar
    python3 scripts/update_jira.py --key PMCP-7  # actualiza solo un issue
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

JSON_FILE = Path(__file__).parent / "jira_descriptions_complete.json"

# ---------------------------------------------------------------------------
# ADF builders
# ---------------------------------------------------------------------------

def _text(content: str, bold: bool = False) -> dict:
    node: dict = {"type": "text", "text": content}
    if bold:
        node["marks"] = [{"type": "strong"}]
    return node


def _paragraph(*inline_nodes) -> dict:
    return {"type": "paragraph", "content": list(inline_nodes)}


def _heading(text: str, level: int = 2) -> dict:
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [_text(text)],
    }


def _bullet_list(items: list[str]) -> dict:
    return {
        "type": "bulletList",
        "content": [
            {
                "type": "listItem",
                "content": [_paragraph(_text(item))],
            }
            for item in items
        ],
    }


def _code_block(code: str, language: str = "text") -> dict:
    return {
        "type": "codeBlock",
        "attrs": {"language": language},
        "content": [{"type": "text", "text": code}],
    }


def _rule() -> dict:
    return {"type": "rule"}


def build_adf(
    description: str,
    acceptance_criteria: list[str],
    prompt: dict | None = None,
) -> dict:
    """Construye un ADF doc con descripción, AC y opcionalmente el prompt."""
    content = []

    # --- Descripción ---
    for para in description.strip().split("\n\n"):
        para = para.strip()
        if para:
            content.append(_paragraph(_text(para)))

    # --- Criterios de aceptación ---
    if acceptance_criteria:
        content.append(_heading("Criterios de aceptación", level=2))
        content.append(_bullet_list(acceptance_criteria))

    # --- Prompt (solo en historias) ---
    if prompt:
        content.append(_rule())
        content.append(_heading("Prompt de implementación", level=2))

        context_items = prompt.get("context") or []
        instruction = (prompt.get("instruction") or "").strip()

        if context_items:
            content.append(_heading("Contexto / ficheros de referencia", level=3))
            content.append(_bullet_list(context_items))

        if instruction:
            content.append(_heading("Instrucción", level=3))
            content.append(_code_block(instruction, language="text"))

    return {"type": "doc", "version": 1, "content": content}


# ---------------------------------------------------------------------------
# Jira client
# ---------------------------------------------------------------------------

class JiraClient:
    def __init__(self, base_url: str, email: str, token: str) -> None:
        self._base = base_url.rstrip("/")
        self._auth = (email, token)
        self._session = requests.Session()
        self._session.auth = self._auth
        self._session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        self._story_points_field: str | None = None  # descubierto lazy

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._base}/rest/api/3/{path.lstrip('/')}"

    def _get(self, path: str, **params) -> dict | None:
        r = self._session.get(self._url(path), params=params, timeout=15)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def _put(self, path: str, body: dict) -> requests.Response:
        return self._session.put(self._url(path), json=body, timeout=15)

    # ------------------------------------------------------------------
    # Story points field discovery
    # ------------------------------------------------------------------

    def discover_story_points_field(self) -> str:
        """Retorna el key del campo Story Points (customfield_XXXXX).
        Intenta primero customfield_10016 y si no existe busca por nombre."""
        # Intentar primero el campo estándar de Jira Cloud
        candidate = "customfield_10016"
        fields = self._get("field") or []
        sp_fields = [
            f for f in fields
            if "story" in f.get("name", "").lower() and "point" in f.get("name", "").lower()
        ]
        if not sp_fields:
            sp_fields = [f for f in fields if f.get("id") == candidate]

        if sp_fields:
            found = sp_fields[0]
            if found["id"] != candidate:
                log.info(
                    "  ℹ️  Campo Story Points encontrado: '%s' → id=%s (no es %s)",
                    found["name"], found["id"], candidate,
                )
            return found["id"]

        log.warning(
            "  ⚠️  No se encontró campo 'Story Points' en la instancia. "
            "Se usará %s por defecto. Si falla, revisa los campos disponibles.",
            candidate,
        )
        return candidate

    def get_story_points_field(self) -> str:
        if self._story_points_field is None:
            self._story_points_field = self.discover_story_points_field()
        return self._story_points_field

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_issue(self, key: str) -> dict | None:
        return self._get(f"issue/{key}", fields="summary,issuetype")

    def update_issue(
        self,
        key: str,
        adf_body: dict,
        story_points: int | None = None,
        dry_run: bool = False,
    ) -> tuple[bool, str]:
        """Actualiza descripción y story_points. Retorna (ok, mensaje)."""
        fields: dict = {"description": adf_body}

        if story_points is not None:
            sp_field = self.get_story_points_field()
            fields[sp_field] = story_points

        if dry_run:
            return True, f"DRY-RUN — se actualizaría con fields={list(fields.keys())}"

        r = self._put(f"issue/{key}", {"fields": fields})

        if r.status_code == 204:
            return True, "OK"

        # Si story_points falla, reintenta solo con descripción
        if r.status_code == 400 and story_points is not None:
            try:
                detail = r.json()
                errors = detail.get("errors", {})
            except Exception:
                errors = {}

            sp_field = self.get_story_points_field()
            if sp_field in errors or "customfield" in str(errors):
                log.warning(
                    "  ⚠️  Story Points (%s) rechazado: %s. Reintentando sin puntos...",
                    sp_field, errors.get(sp_field, errors),
                )
                r2 = self._put(f"issue/{key}", {"fields": {"description": adf_body}})
                if r2.status_code == 204:
                    return True, f"OK (sin puntos — {sp_field} no aceptado por este tipo de issue)"
                return False, f"HTTP {r2.status_code}: {r2.text[:200]}"

        try:
            detail = r.json()
        except Exception:
            detail = r.text[:300]
        return False, f"HTTP {r.status_code}: {detail}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Actualiza Jira desde jira_descriptions_complete.json")
    p.add_argument("--dry-run", action="store_true", help="Muestra cambios sin ejecutar")
    p.add_argument("--key", metavar="PMCP-X", help="Actualiza solo este issue")
    return p.parse_args()


def iter_issues(data: dict):
    """Genera tuplas (issue_dict, is_epic) para todos los epics e historias."""
    for epic in data["epics"]:
        yield epic, True
        for task in epic.get("tasks", []):
            yield task, False


def main() -> int:
    args = parse_args()

    # Credenciales
    jira_url = os.getenv("JIRA_URL") or os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")

    missing = [k for k, v in [("JIRA_URL", jira_url), ("JIRA_EMAIL", email), ("JIRA_API_TOKEN", token)] if not v]
    if missing:
        log.error("Faltan variables de entorno: %s", ", ".join(missing))
        return 1

    if not JSON_FILE.exists():
        log.error("No se encuentra %s", JSON_FILE)
        return 1

    with JSON_FILE.open(encoding="utf-8") as f:
        data = json.load(f)

    client = JiraClient(jira_url, email, token)

    if args.dry_run:
        log.info("🔍 DRY-RUN activado — no se realizarán cambios en Jira\n")

    # Pre-descubrir el campo Story Points (evita una llamada extra por issue)
    sp_field = client.get_story_points_field()
    log.info("📋 Campo Story Points: %s\n", sp_field)

    ok_count = 0
    skip_count = 0
    fail_count = 0
    issues_to_process = list(iter_issues(data))

    # Filtrar por --key si se especificó
    if args.key:
        issues_to_process = [(iss, is_epic) for iss, is_epic in issues_to_process if iss["key"] == args.key]
        if not issues_to_process:
            log.error("Issue %s no encontrado en el JSON", args.key)
            return 1

    for issue, is_epic in issues_to_process:
        key = issue["key"]
        label = "EPIC" if is_epic else "HIST"

        sys.stdout.write(f"  [{label}] Actualizando {key}... ")
        sys.stdout.flush()

        # Verificar que existe en Jira
        existing = client.get_issue(key)
        if existing is None:
            print("SKIP — no existe en Jira")
            skip_count += 1
            continue

        # Construir ADF
        prompt = issue.get("prompt")  # None en epics
        adf = build_adf(
            description=issue.get("description", ""),
            acceptance_criteria=issue.get("acceptance_criteria", []),
            prompt=prompt,
        )

        # Story points: solo historias (epics tienen total_story_points, no story_points)
        sp = issue.get("story_points") if not is_epic else None

        ok, msg = client.update_issue(key, adf, story_points=sp, dry_run=args.dry_run)

        if ok:
            print(msg)
            ok_count += 1
        else:
            print(f"FAIL — {msg}")
            fail_count += 1

    # Resumen
    print()
    total = ok_count + skip_count + fail_count
    print(f"{'─' * 45}")
    print(f"  Total procesados : {total}")
    print(f"  ✅ Actualizados  : {ok_count}")
    print(f"  ⏭️  Omitidos      : {skip_count}  (no existen en Jira)")
    print(f"  ❌ Fallidos      : {fail_count}")
    print(f"{'─' * 45}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
