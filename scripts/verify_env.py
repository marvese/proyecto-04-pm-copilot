#!/usr/bin/env python3
"""verify_env.py — Verifica que todos los servicios de PM Copilot están listos.

Comprueba: variables .env, PostgreSQL (tablas), ChromaDB, LLM provider.
Exit code 0 = todo OK. Exit code 1 = algún fallo.

Uso: python3 scripts/verify_env.py
"""
import asyncio
import os
import sys

import requests
from dotenv import dotenv_values

REQUIRED_VARS = [
    "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD",
    "POSTGRES_PORT", "DATABASE_URL",
    "CHROMADB_HOST", "CHROMADB_PORT",
]
PLACEHOLDER_MARKERS = {"<token>", "AIza...", "sk-ant-...", "gsk_...", "ghp_...", "<tu-instancia>"}
EXPECTED_TABLES = {
    "projects", "sprints", "tasks", "estimations",
    "knowledge_chunks", "chat_sessions", "chat_messages",
}

OK = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"

results: list[tuple[str, bool, str]] = []


def check(label: str, passed: bool, detail: str = "") -> bool:
    results.append((label, passed, detail))
    symbol = OK if passed else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  {symbol} {label}{suffix}")
    return passed


# ── 1. Variables de entorno ───────────────────────────────────────────────────

def check_env_vars(env: dict) -> None:
    print("\n[1] Variables de entorno")
    for var in REQUIRED_VARS:
        val = env.get(var, "")
        if not val:
            check(var, False, "ausente")
        elif any(p in val for p in PLACEHOLDER_MARKERS):
            check(var, False, "valor placeholder sin rellenar")
        else:
            check(var, True)


# ── 2. PostgreSQL ─────────────────────────────────────────────────────────────

async def check_postgres(env: dict) -> None:
    import asyncpg

    print("\n[2] PostgreSQL")
    url = env.get("DATABASE_URL", "")
    if not url:
        check("Conexión", False, "DATABASE_URL no definida")
        check("Tablas", False, "sin conexión")
        return

    # asyncpg no acepta el scheme SQLAlchemy postgresql+asyncpg://
    asyncpg_url = url.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(asyncpg_url, timeout=5)
    except Exception as exc:
        check("Conexión", False, str(exc)[:80])
        check("Tablas", False, "sin conexión")
        return

    check("Conexión (SELECT 1)", True)

    try:
        rows = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        found = {r["tablename"] for r in rows}
        missing = EXPECTED_TABLES - found
        if missing:
            check("Tablas", False, f"faltan: {', '.join(sorted(missing))}")
        else:
            check("Tablas (7/7)", True)
    finally:
        await conn.close()


# ── 3. ChromaDB ───────────────────────────────────────────────────────────────

def check_chromadb(env: dict) -> None:
    print("\n[3] ChromaDB")
    host = env.get("CHROMADB_HOST", "localhost")
    port = env.get("CHROMADB_PORT", "8001")
    url = f"http://{host}:{port}/api/v2/heartbeat"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            check(f"Heartbeat ({url})", True)
        else:
            check(f"Heartbeat ({url})", False, f"HTTP {resp.status_code}")
    except Exception as exc:
        check(f"Heartbeat ({url})", False, str(exc)[:80])


# ── 4. LLM provider ──────────────────────────────────────────────────────────

def check_llm(env: dict) -> None:
    print("\n[4] LLM provider")
    mode = env.get("LLM_MODE", "local").lower()
    check(f"LLM_MODE={mode}", True)

    if mode == "local":
        ollama_url = env.get("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if resp.status_code != 200:
                check("Ollama responde", False, f"HTTP {resp.status_code}")
                return
            check("Ollama responde", True)
            models = [m["name"] for m in resp.json().get("models", [])]
            has_embed = any("nomic-embed-text" in m for m in models)
            check(
                "nomic-embed-text disponible",
                has_embed,
                "" if has_embed else f"modelos actuales: {', '.join(models) or 'ninguno'}",
            )
        except Exception as exc:
            check("Ollama responde", False, str(exc)[:80])
    else:
        anthropic_key = env.get("ANTHROPIC_API_KEY", "")
        is_real = anthropic_key and not any(p in anthropic_key for p in PLACEHOLDER_MARKERS)
        check("ANTHROPIC_API_KEY presente", bool(is_real))


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> int:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env = dotenv_values(env_path)

    check_env_vars(env)
    await check_postgres(env)
    check_chromadb(env)
    check_llm(env)

    failures = [label for label, passed, _ in results if not passed]
    print()
    if failures:
        print(f"\033[31mFallaron {len(failures)} verificación(es): {', '.join(failures)}\033[0m")
        return 1
    print(f"\033[32mTodo OK — entorno listo para PM Copilot.\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
