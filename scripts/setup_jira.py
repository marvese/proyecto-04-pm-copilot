#!/usr/bin/env python3
"""setup_jira.py — Crea el proyecto Jira 'PM Copilot' con épicas e historias.

Idempotente: si el proyecto o los issues ya existen, los omite sin duplicar.
Lee del .env: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

PROJECT_KEY = "PMCP"
PROJECT_NAME = "PM Copilot"
PROJECT_DESCRIPTION = (
    "PM Copilot — Asistente inteligente con RAG para gestión de proyectos de software. "
    "Arquitectura hexagonal, FastAPI, React PWA, LLM Router con Claude + Ollama."
)

AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

# ---------------------------------------------------------------------------
# Backlog: 9 épicas con sus historias
# ---------------------------------------------------------------------------

BACKLOG: list[dict[str, Any]] = [
    {
        "epic": "Infraestructura base",
        "description": (
            "Docker Compose local con PostgreSQL y ChromaDB, DDL de tablas, "
            ".env.example y script de verificación del entorno."
        ),
        "stories": [
            "Crear docker-compose con PostgreSQL + ChromaDB",
            "DDL de tablas (tasks, projects, sprints, estimations)",
            "Crear .env.example completo",
            "Script de arranque y verificación del entorno",
        ],
    },
    {
        "epic": "LLM Core",
        "description": (
            "Adaptadores LLM (Claude y Ollama) y LLMRouter con fallback automático "
            "via tenacity. Base de toda la capa de generación del sistema."
        ),
        "stories": [
            "Implementar ClaudeAdapter (texto + streaming)",
            "Implementar LLMRouter con fallback y tenacity",
            "Tests unitarios del router",
            "Implementar OllamaLLMAdapter para modo local",
        ],
    },
    {
        "epic": "Primer caso de uso vertical: EstimateTask",
        "description": (
            "Slice vertical completo: EstimationService en dominio, use case, "
            "endpoint REST /estimate funcional con RAG y tests de integración."
        ),
        "stories": [
            "Implementar EstimationService en dominio",
            "Implementar EstimateTask use case",
            "Endpoint REST /estimate funcional",
            "Tests de integración del caso de uso",
        ],
    },
    {
        "epic": "Chat con streaming",
        "description": (
            "Conversación en tiempo real: WebSocket handler con streaming de tokens, "
            "hook useCopilotChat y componente Chat conectado al backend."
        ),
        "stories": [
            "Implementar QueryProjectStatus use case",
            "WebSocket handler con streaming real",
            "useCopilotChat hook en frontend",
            "Componente Chat funcional conectado al backend",
        ],
    },
    {
        "epic": "RAG y base de conocimiento",
        "description": (
            "Pipeline completo de RAG: embeddings con nomic-embed-text via Ollama, "
            "ChromaDB como vector store, indexación de documentos y queries con citas."
        ),
        "stories": [
            "Implementar OllamaEmbeddingAdapter",
            "Implementar ChromaDBAdapter",
            "IndexDocuments use case",
            "QueryKnowledge use case",
            "Tests de integración RAG",
        ],
    },
    {
        "epic": "Persistencia",
        "description": (
            "Adaptadores PostgreSQL para Tasks, Projects y Sprints, "
            "migraciones con Alembic y tests de repositorios contra BD real."
        ),
        "stories": [
            "Implementar PostgreSQLTaskAdapter",
            "Implementar PostgreSQLProjectAdapter + Sprint",
            "Migraciones con Alembic",
            "Tests de repositorios",
        ],
    },
    {
        "epic": "Integraciones externas",
        "description": (
            "Adaptadores para Jira (sync bidireccional), Confluence (publicar informes) "
            "y GitHub (leer PRs/commits). Todos con Circuit Breaker via tenacity."
        ),
        "stories": [
            "Implementar JiraAdapter (sync bidireccional)",
            "Implementar ConfluenceAdapter (publicar reportes)",
            "Implementar GitHubAdapter (leer PRs/commits)",
            "SyncJira use case",
        ],
    },
    {
        "epic": "Frontend completo",
        "description": (
            "Dashboard con métricas, página de Tasks y Reports conectadas al backend, "
            "y configuración PWA con manifest y service worker."
        ),
        "stories": [
            "Dashboard con métricas del proyecto",
            "Página de Tasks conectada al backend",
            "Página de Reports con generación bajo demanda",
            "PWA: manifest + service worker",
        ],
    },
    {
        "epic": "Calidad y despliegue",
        "description": (
            "Cobertura de tests al 80%, pipeline CI con GitHub Actions, "
            "Dockerfiles para backend y frontend, y documentación de despliegue."
        ),
        "stories": [
            "Configurar pytest con cobertura mínima 80%",
            "GitHub Actions: CI con tests + lint",
            "Dockerfile para backend y frontend",
            "Documentación de despliegue en Confluence",
        ],
    },
]

# ---------------------------------------------------------------------------
# HTTP wrapper
# ---------------------------------------------------------------------------

def _api(method: str, path: str, **kwargs: Any) -> Any:
    """Wrapper con manejo de errores descriptivo. path puede ser absoluto o relativo."""
    if path.startswith("http"):
        url = path
    elif path.startswith("/rest"):
        url = f"{JIRA_URL}{path}"
    else:
        url = f"{JIRA_URL}/rest/api/3/{path.lstrip('/')}"

    resp = requests.request(
        method, url, auth=AUTH, headers=HEADERS, timeout=20, **kwargs
    )
    if not resp.ok:
        print(f"\n  [!] Error {resp.status_code} {method} {url}")
        try:
            detail = resp.json()
            msgs = detail.get("errorMessages") or list(detail.get("errors", {}).values())
            print(f"      {' | '.join(str(m) for m in msgs) or resp.text[:300]}")
        except Exception:
            print(f"      {resp.text[:300]}")
        resp.raise_for_status()
    return resp.json() if resp.content else {}


def _validate_config() -> None:
    missing = [
        name
        for name, val in [
            ("JIRA_URL", JIRA_URL),
            ("JIRA_EMAIL", JIRA_EMAIL),
            ("JIRA_API_TOKEN", JIRA_API_TOKEN),
        ]
        if not val
    ]
    if missing:
        sys.exit(f"Error: faltan variables de entorno: {', '.join(missing)}")


# ---------------------------------------------------------------------------
# Usuario autenticado
# ---------------------------------------------------------------------------

def get_myself() -> dict[str, Any]:
    return _api("GET", "/rest/api/3/myself")


# ---------------------------------------------------------------------------
# Proyecto
# ---------------------------------------------------------------------------

def find_project(key: str) -> dict[str, Any] | None:
    try:
        return _api("GET", f"project/{key}")
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            return None
        raise


def create_project(lead_account_id: str) -> dict[str, Any]:
    return _api(
        "POST",
        "project",
        json={
            "key": PROJECT_KEY,
            "name": PROJECT_NAME,
            "description": PROJECT_DESCRIPTION,
            "projectTypeKey": "software",
            "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-scrum-template",
            "leadAccountId": lead_account_id,
            "assigneeType": "PROJECT_LEAD",
        },
    )


def ensure_project(lead_account_id: str) -> tuple[dict[str, Any], str]:
    existing = find_project(PROJECT_KEY)
    if existing:
        return existing, "existing"
    project = create_project(lead_account_id)
    return project, "created"


# ---------------------------------------------------------------------------
# Descubrimiento de campos custom
# ---------------------------------------------------------------------------

_FIELD_CACHE: list[dict[str, Any]] | None = None


def _all_fields() -> list[dict[str, Any]]:
    global _FIELD_CACHE
    if _FIELD_CACHE is None:
        _FIELD_CACHE = _api("GET", "field")
    return _FIELD_CACHE


def _find_field(custom_type: str, fallback_name: str) -> str | None:
    """Returns field key matching the Jira custom type or display name, or None."""
    for field in _all_fields():
        schema = field.get("schema", {})
        if schema.get("custom") == custom_type:
            return field["key"]
    for field in _all_fields():
        if field.get("name") == fallback_name:
            return field["key"]
    return None


def discover_epic_fields() -> tuple[str | None, str | None]:
    """Returns (epic_link_field_key, epic_name_field_key)."""
    epic_link = _find_field(
        "com.pyxis.greenhopper.jira:gh-epic-link", "Epic Link"
    )
    epic_name = _find_field(
        "com.pyxis.greenhopper.jira:gh-epic-label", "Epic Name"
    )
    return epic_link, epic_name


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def _search_exact(summary: str, issue_type: str) -> dict[str, Any] | None:
    """Searches for an issue by exact summary. Returns first exact match or None."""
    # JQL tilde (~) does substring search; we post-filter for exact match
    safe = summary.replace("\\", "\\\\").replace('"', '\\"')
    jql = f'project = "{PROJECT_KEY}" AND issuetype = "{issue_type}" AND summary ~ "{safe}"'
    try:
        resp = _api(
            "GET",
            "search/jql",  # /rest/api/3/search fue eliminado en 2024 (CHANGE-2046)
            params={"jql": jql, "maxResults": 10, "fields": "summary,key"},
        )
    except requests.HTTPError:
        return None
    for issue in resp.get("issues", []):
        if issue["fields"]["summary"].strip() == summary.strip():
            return issue
    return None


def create_epic(
    title: str,
    description: str,
    epic_name_field: str | None,
) -> tuple[dict[str, Any], str]:
    existing = _search_exact(title, "Epic")
    if existing:
        return existing, "existing"

    fields: dict[str, Any] = {
        "project": {"key": PROJECT_KEY},
        "summary": title,
        "description": _adf(description),
        "issuetype": {"name": "Epic"},
    }
    if epic_name_field:
        # Classic Jira: Epic Name field required for board display
        fields[epic_name_field] = title

    issue = _api("POST", "issue", json={"fields": fields})
    return issue, "created"


def create_story(
    summary: str,
    epic_key: str,
    epic_link_field: str | None,
) -> tuple[dict[str, Any], str]:
    existing = _search_exact(summary, "Story")
    if existing:
        return existing, "existing"

    # Strategy 1: classic Epic Link custom field
    if epic_link_field:
        fields: dict[str, Any] = {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "issuetype": {"name": "Story"},
            epic_link_field: epic_key,
        }
        try:
            issue = _api("POST", "issue", json={"fields": fields})
            return issue, "created"
        except requests.HTTPError:
            pass  # fall through to next strategy

    # Strategy 2: parent field (next-gen / team-managed)
    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "issuetype": {"name": "Story"},
        "parent": {"key": epic_key},
    }
    try:
        issue = _api("POST", "issue", json={"fields": fields})
        return issue, "created"
    except requests.HTTPError:
        pass

    # Strategy 3: create without link, then link via Agile API
    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "issuetype": {"name": "Story"},
    }
    issue = _api("POST", "issue", json={"fields": fields})
    story_key = issue.get("key", "")
    linked = _link_via_agile_api(story_key, epic_key)
    action = "created" if linked else "created (sin epic link)"
    return issue, action


def _link_via_agile_api(story_key: str, epic_key: str) -> bool:
    """Uses Jira Agile API to link a story to an epic. Returns True on success."""
    try:
        _api(
            "POST",
            f"/rest/agile/1.0/epic/{epic_key}/issue",
            json={"issues": [story_key]},
        )
        return True
    except Exception:
        return False


def _adf(text: str) -> dict[str, Any]:
    """Wraps plain text in Atlassian Document Format (ADF) for description fields."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            }
        ],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _validate_config()
    print(f"Conectando a {JIRA_URL}\n")

    # Autenticación
    me = get_myself()
    account_id: str = me["accountId"]
    display_name: str = me.get("displayName", me.get("emailAddress", "?"))
    print(f"  Autenticado como: {display_name}\n")

    # Proyecto
    print(f"Verificando proyecto {PROJECT_KEY}...")
    project, proj_action = ensure_project(account_id)
    proj_icon = "+" if proj_action == "created" else "✓"
    print(f"  [{proj_icon}] {PROJECT_NAME} ({PROJECT_KEY}) — {proj_action}")
    print(f"       {JIRA_URL}/jira/software/projects/{PROJECT_KEY}/boards\n")

    # Campos custom
    print("Descubriendo campos custom...")
    epic_link_field, epic_name_field = discover_epic_fields()
    print(f"  Epic Link field : {epic_link_field or 'no encontrado — usando parent / Agile API'}")
    print(f"  Epic Name field : {epic_name_field or 'no encontrado — omitido'}\n")

    # Épicas e historias
    epics_created = 0
    epics_existing = 0
    stories_created = 0
    stories_existing = 0
    results: list[dict[str, Any]] = []

    total = len(BACKLOG)
    for idx, item in enumerate(BACKLOG, start=1):
        epic_title: str = item["epic"]
        description: str = item["description"]
        story_titles: list[str] = item["stories"]

        print(f"[{idx}/{total}] Épica: {epic_title}")
        epic, epic_action = create_epic(epic_title, description, epic_name_field)
        epic_key: str = epic.get("key", "?")
        epic_icon = "+" if epic_action == "created" else "✓"
        print(f"  [{epic_icon}] {epic_key}  {epic_title} ({epic_action})")

        if epic_action == "created":
            epics_created += 1
        else:
            epics_existing += 1

        story_keys: list[str] = []
        for story_title in story_titles:
            story, story_action = create_story(story_title, epic_key, epic_link_field)
            story_key: str = story.get("key", "?")
            s_icon = "+" if story_action.startswith("created") else "✓"
            note = " ⚠" if "sin epic link" in story_action else ""
            print(f"    [{s_icon}] {story_key}  {story_title}{note}")

            if story_action.startswith("created"):
                stories_created += 1
            else:
                stories_existing += 1
            story_keys.append(story_key)

        results.append(
            {
                "epic_key": epic_key,
                "epic_title": epic_title,
                "story_keys": story_keys,
            }
        )
        print()

    # Resumen
    total_epics = epics_created + epics_existing
    total_stories = stories_created + stories_existing

    print("─" * 60)
    print(f"  Épicas   : {epics_created:2d} creadas, {epics_existing:2d} ya existían → {total_epics:2d} total")
    print(f"  Historias: {stories_created:2d} creadas, {stories_existing:2d} ya existían → {total_stories:2d} total")
    print()
    print("  Backlog creado:")
    for r in results:
        stories_str = ", ".join(r["story_keys"])
        print(f"    {r['epic_key']:<10} {r['epic_title']}")
        print(f"    {'':10} Historias: {stories_str}")
    print()
    print(f"  Backlog  → {JIRA_URL}/jira/software/projects/{PROJECT_KEY}/boards")
    print(f"  Roadmap  → {JIRA_URL}/jira/software/projects/{PROJECT_KEY}/roadmap")
    print()


if __name__ == "__main__":
    main()
