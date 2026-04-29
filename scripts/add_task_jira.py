"""add_task_jira.py — Crea un issue Story en Jira con descripción ADF completa.

Uso:
    python3 scripts/add_task_jira.py
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# ADF builders (misma implementación que update_jira.py)
# ---------------------------------------------------------------------------

def _text(content: str) -> dict:
    return {"type": "text", "text": content}


def _paragraph(text: str) -> dict:
    return {"type": "paragraph", "content": [_text(text)]}


def _heading(text: str, level: int = 2) -> dict:
    return {"type": "heading", "attrs": {"level": level}, "content": [_text(text)]}


def _bullet_list(items: list[str]) -> dict:
    return {
        "type": "bulletList",
        "content": [
            {"type": "listItem", "content": [_paragraph(item)]}
            for item in items
        ],
    }


def _code_block(code: str) -> dict:
    return {
        "type": "codeBlock",
        "attrs": {"language": "text"},
        "content": [{"type": "text", "text": code}],
    }


def _rule() -> dict:
    return {"type": "rule"}


def build_adf(description: str, acceptance_criteria: list[str],
              prompt_context: list[str], prompt_instruction: str,
              estimation_vibe: dict | None = None,
              estimation_human: dict | None = None) -> dict:
    content = []

    for para in description.strip().split("\n\n"):
        para = para.strip()
        if para:
            content.append(_paragraph(para))

    content.append(_heading("Criterios de aceptación", level=2))
    content.append(_bullet_list(acceptance_criteria))

    if estimation_vibe or estimation_human:
        content.append(_rule())
        content.append(_heading("Estimaciones", level=2))
        rows = []
        if estimation_vibe:
            rows.append(
                f"🤖 Vibe coding (Claude Code): {estimation_vibe['hours']}h — {estimation_vibe['notes']}"
            )
        if estimation_human:
            rows.append(
                f"👤 Senior sin IA: {estimation_human['hours']}h — {estimation_human['notes']}"
            )
        content.append(_bullet_list(rows))

    content.append(_rule())
    content.append(_heading("Prompt de implementación", level=2))
    content.append(_heading("Contexto / ficheros de referencia", level=3))
    content.append(_bullet_list(prompt_context))
    content.append(_heading("Instrucción", level=3))
    content.append(_code_block(prompt_instruction))

    return {"type": "doc", "version": 1, "content": content}


# ---------------------------------------------------------------------------
# Issue definition
# ---------------------------------------------------------------------------

ISSUE = {
    "summary": "Tabla llm_usage y logging de consumo por llamada",
    "epic_key": "PMCP-6",
    "story_points": 3,
    "description": (
        "Crear tabla llm_usage en PostgreSQL para registrar el consumo real de cada "
        "llamada LLM: tokens de entrada y salida, coste estimado en USD, modelo usado, "
        "LLMTaskType y latencia en milisegundos.\n\n"
        "El logging debe ser automático en ClaudeAdapter: tras cada llamada exitosa a "
        "complete() y stream(), insertar una fila en llm_usage sin bloquear el flujo "
        "principal (fire-and-forget con asyncio.create_task o similar). El DDL se añade "
        "a scripts/db_init.sql y la fixture al conftest.py de tests."
    ),
    "acceptance_criteria": [
        "Tabla llm_usage creada en db_init.sql con columnas: id UUID PK, adapter VARCHAR, "
        "model VARCHAR, task_type VARCHAR, input_tokens INT, output_tokens INT, "
        "estimated_cost_usd FLOAT, latency_ms INT, created_at TIMESTAMPTZ",
        "Índices en (adapter, created_at), (task_type, created_at) y created_at DESC",
        "ClaudeAdapter.complete() inserta fila en llm_usage tras respuesta exitosa",
        "ClaudeAdapter.stream() inserta fila con token count acumulado al finalizar el stream",
        "Fixture mock_llm_usage_log disponible en backend/tests/conftest.py",
        "Query SELECT adapter, task_type, SUM(input_tokens+output_tokens), AVG(latency_ms) "
        "GROUP BY adapter, task_type retorna datos correctos en test de integración",
    ],
    "prompt_context": [
        "backend/src/adapters/secondary/llm/claude_adapter.py",
        "backend/src/domain/ports/llm_port.py  (LLMRequest, LLMResponse, LLMTaskType)",
        "scripts/db_init.sql",
        "backend/tests/conftest.py",
    ],
    "estimation_vibe_coding": {
        "hours": 1.5,
        "notes": (
            "DDL de la tabla es directo. El logging en ClaudeAdapter con asyncio.create_task "
            "y el cálculo de coste por modelo requieren una iteración de ajuste. "
            "La fixture en conftest.py es trivial."
        ),
    },
    "estimation_human": {
        "hours": 5,
        "notes": (
            "El senior debe diseñar la fórmula de coste (precio por Mtok varía por modelo), "
            "implementar el logging no bloqueante con asyncio.create_task sin race conditions, "
            "y escribir el test de integración que verifica la query de agregación."
        ),
    },
    "prompt_instruction": (
        "Añade la tabla llm_usage a scripts/db_init.sql:\n"
        "  CREATE TABLE IF NOT EXISTS llm_usage (\n"
        "      id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),\n"
        "      adapter          VARCHAR(32) NOT NULL,  -- 'anthropic'|'groq'|'gemini'|'ollama'\n"
        "      model            VARCHAR(64) NOT NULL,\n"
        "      task_type        VARCHAR(32) NOT NULL,  -- LLMTaskType value\n"
        "      input_tokens     INT         NOT NULL DEFAULT 0,\n"
        "      output_tokens    INT         NOT NULL DEFAULT 0,\n"
        "      estimated_cost_usd FLOAT     NOT NULL DEFAULT 0.0,\n"
        "      latency_ms       INT         NOT NULL DEFAULT 0,\n"
        "      created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()\n"
        "  );\n"
        "  CREATE INDEX IF NOT EXISTS idx_llm_usage_adapter   ON llm_usage (adapter, created_at DESC);\n"
        "  CREATE INDEX IF NOT EXISTS idx_llm_usage_task_type ON llm_usage (task_type, created_at DESC);\n\n"
        "En ClaudeAdapter (backend/src/adapters/secondary/llm/claude_adapter.py):\n"
        "  - Añade parámetro opcional usage_repo al constructor (puede ser None).\n"
        "  - En complete(): registra start = time.monotonic() antes de la llamada, "
        "calcula latency_ms = int((time.monotonic()-start)*1000), calcula "
        "estimated_cost_usd según el modelo (claude-sonnet-4-6: input $3/Mtok, "
        "output $15/Mtok), llama asyncio.create_task(usage_repo.log(...)) si usage_repo.\n"
        "  - En stream(): acumula output_tokens contando los tokens del stream, "
        "registra al finalizar con el mismo patrón.\n\n"
        "En backend/tests/conftest.py añade:\n"
        "  @pytest.fixture\n"
        "  def mock_llm_usage_log():\n"
        "      return AsyncMock()  # simula el repositorio de logging"
    ),
}

# Campos Jira (descubiertos via GET /rest/api/3/field en esta instancia)
EPIC_LINK_FIELD = "customfield_10014"
STORY_POINTS_FIELD = "customfield_10032"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    base = os.getenv("JIRA_URL") or os.getenv("JIRA_BASE_URL", "")
    email = os.getenv("JIRA_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")

    missing = [k for k, v in [("JIRA_URL", base), ("JIRA_EMAIL", email), ("JIRA_API_TOKEN", token)] if not v]
    if missing:
        print(f"ERROR: Faltan variables de entorno: {', '.join(missing)}")
        return 1

    auth = (email, token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    adf = build_adf(
        description=ISSUE["description"],
        acceptance_criteria=ISSUE["acceptance_criteria"],
        prompt_context=ISSUE["prompt_context"],
        prompt_instruction=ISSUE["prompt_instruction"],
        estimation_vibe=ISSUE.get("estimation_vibe_coding"),
        estimation_human=ISSUE.get("estimation_human"),
    )

    payload = {
        "fields": {
            "project": {"key": "PMCP"},
            "issuetype": {"name": "Historia"},
            "summary": ISSUE["summary"],
            "description": adf,
            EPIC_LINK_FIELD: ISSUE["epic_key"],
            STORY_POINTS_FIELD: ISSUE["story_points"],
        }
    }

    print(f"Creando issue '{ISSUE['summary']}'...")
    r = requests.post(
        f"{base}/rest/api/3/issue",
        json=payload,
        auth=auth,
        headers=headers,
        timeout=15,
    )

    if r.status_code == 201:
        key = r.json()["key"]
        print(f"✅ Issue creado: {key}")
        print(f"   Epic: {ISSUE['epic_key']}  |  Story Points: {ISSUE['story_points']}")
        print(f"   URL: {base}/browse/{key}")
        return 0

    # Fallo — intentar sin EPIC_LINK_FIELD si ese fue el problema
    try:
        detail = r.json()
        errors = detail.get("errors", {})
    except Exception:
        errors = {}

    if EPIC_LINK_FIELD in errors:
        print(f"⚠️  Epic Link ({EPIC_LINK_FIELD}) rechazado: {errors[EPIC_LINK_FIELD]}")
        print("   Reintentando sin epic link (vincula manualmente desde Jira)...")
        del payload["fields"][EPIC_LINK_FIELD]
        r2 = requests.post(
            f"{base}/rest/api/3/issue",
            json=payload,
            auth=auth,
            headers=headers,
            timeout=15,
        )
        if r2.status_code == 201:
            key = r2.json()["key"]
            print(f"✅ Issue creado: {key}  (vincula manualmente a {ISSUE['epic_key']})")
            print(f"   URL: {base}/browse/{key}")
            return 0
        print(f"❌ Segundo intento fallido: HTTP {r2.status_code} — {r2.text[:300]}")
        return 1

    print(f"❌ Error HTTP {r.status_code}: {r.text[:400]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
