import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
EMAIL = os.getenv("CONFLUENCE_EMAIL")
API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

AUTH = (EMAIL, API_TOKEN)
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

PAGES = [
    ("01. Metodología PM con IA", "Esta sección describe la metodología de gestión de proyectos apoyada en inteligencia artificial que se desarrolla en este proyecto."),
    ("02. Diario de Desarrollo", "Registro cronológico del proceso de desarrollo, decisiones tomadas y aprendizajes obtenidos durante el proyecto."),
    ("03. Herramientas y Configuración", "Documentación de las herramientas utilizadas, su configuración y la integración entre ellas en el ecosistema del proyecto."),
    ("04. Lecciones Aprendidas", "Compilación de lecciones aprendidas, errores cometidos y buenas prácticas identificadas a lo largo del proyecto."),
    ("05. Playbook: Vibe Coding", "Guía práctica del enfoque Vibe Coding aplicado a este proyecto: flujos de trabajo, prompts efectivos y patrones reutilizables."),
    ("06. PM Copilot — Documentación Técnica", "Documentación técnica del sistema PM Copilot: arquitectura, componentes, APIs y decisiones de diseño."),
]


def get_root_page():
    url = f"{BASE_URL}/rest/api/content"
    # Find the root page (no ancestors) in the space
    params = {
        "spaceKey": SPACE_KEY,
        "type": "page",
        "expand": "ancestors",
        "limit": 50,
    }
    resp = requests.get(url, auth=AUTH, headers=HEADERS, params=params)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    root_pages = [p for p in results if not p.get("ancestors")]
    if not root_pages:
        sys.exit(f"No se encontró ninguna página raíz en el espacio {SPACE_KEY}.")
    page = root_pages[0]
    print(f"Página raíz encontrada: '{page['title']}' (id={page['id']})")
    return page["id"]


def page_exists(title):
    url = f"{BASE_URL}/rest/api/content"
    params = {"spaceKey": SPACE_KEY, "title": title, "type": "page"}
    resp = requests.get(url, auth=AUTH, headers=HEADERS, params=params)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0]["id"] if results else None


def create_page(parent_id, title, intro):
    existing_id = page_exists(title)
    if existing_id:
        print(f"  Ya existe: '{title}' (id={existing_id}) — omitiendo.")
        return existing_id

    body = {
        "type": "page",
        "title": title,
        "space": {"key": SPACE_KEY},
        "ancestors": [{"id": parent_id}],
        "body": {
            "storage": {
                "value": f"<p>{intro}</p>",
                "representation": "storage",
            }
        },
    }
    url = f"{BASE_URL}/rest/api/content"
    resp = requests.post(url, auth=AUTH, headers=HEADERS, data=json.dumps(body))
    resp.raise_for_status()
    page = resp.json()
    print(f"  Creada: '{page['title']}' (id={page['id']})")
    return page["id"]


def main():
    print(f"Conectando a {BASE_URL} — espacio {SPACE_KEY}\n")
    root_id = get_root_page()
    print()
    for title, intro in PAGES:
        create_page(root_id, title, intro)
    print("\nListo.")


if __name__ == "__main__":
    main()
