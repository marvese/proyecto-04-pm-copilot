# Guía de instalación — PM Copilot

## Prerrequisitos

| Herramienta | Versión mínima | Notas |
|---|---|---|
| Python | 3.12 | `python3 --version` |
| Node.js | 20 LTS | `node --version` |
| Docker + Docker Compose | 24 / 2.x | `docker --version && docker compose version` |
| Git | 2.40+ | `git --version` |
| Ollama | 0.3+ | Opcional — solo para `LLM_MODE=local` |

## 1. Clonar el repositorio

```bash
git clone <repo-url> proyecto-04-pm-copilot
cd proyecto-04-pm-copilot
```

## 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y rellena como mínimo:

```env
# Obligatorio para arrancar el backend
POSTGRES_PASSWORD=tu_password
DATABASE_URL=postgresql+asyncpg://pmcopilot:tu_password@localhost:5432/pmcopilot

# LLM — elige un modo
LLM_MODE=local          # Solo Ollama (sin coste)
# LLM_MODE=hybrid       # Claude para razonamiento + Ollama para el resto
# LLM_MODE=cloud        # Claude + Groq + Gemini

# Si LLM_MODE != local
ANTHROPIC_API_KEY=sk-ant-...
```

Las demás variables tienen valores por defecto funcionales para desarrollo local.

## 3. Levantar infraestructura (PostgreSQL + ChromaDB)

```bash
make up       # arranca contenedores en segundo plano
make db-init  # aplica el DDL completo (7 tablas, índices, triggers)
```

Verifica que todo está OK:

```bash
make verify
```

Salida esperada: todos los checks con `✓`.

## 4. Instalar backend

```bash
cd backend
pip install -e ".[dev]"
cd ..
```

Instala FastAPI, SQLAlchemy, anthropic, httpx, tenacity, pytest y herramientas de desarrollo.

> **Nota WSL2**: si `pip install` falla con "externally managed", añade `--break-system-packages`
> o crea un entorno virtual: `python3 -m venv .venv && source .venv/bin/activate`

## 5. Instalar frontend

```bash
cd frontend
npm install
cd ..
```

`npm install` descarga todas las dependencias, incluidos `vite-plugin-pwa` y `recharts`. El proxy de desarrollo está preconfigurado en `vite.config.ts`: cualquier petición a `/api` se redirige a `http://localhost:8000`.

Variable de entorno opcional del frontend (`.env` o `.env.local` dentro de `frontend/`):

```env
VITE_API_URL=http://localhost:8000   # URL base del backend (por defecto http://localhost:8080)
```

## 6. Verificar instalación completa

```bash
# Infraestructura
make verify

# Tests backend (sin integración)
cd backend && python3 -m pytest -m "not integration" -v

# Servidor de desarrollo backend
cd backend && uvicorn src.main:app --reload --port 8000

# Servidor de desarrollo frontend
cd frontend && npm run dev
```

El backend queda disponible en `http://localhost:8000` y el frontend en `http://localhost:5173`.

## 7. Instalar Ollama (modo local — opcional)

Ollama es necesario si `LLM_MODE=local` o como fallback en modo `hybrid`.

```bash
# Linux / WSL2
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelos necesarios
ollama pull llama3.2          # modelo de generación
ollama pull nomic-embed-text  # embeddings para RAG
```

Verifica que los modelos están disponibles:

```bash
ollama list
# Debe aparecer: llama3.2, nomic-embed-text
```

## 8. Build de producción del frontend

```bash
cd frontend
npm run build    # genera dist/ optimizado con PWA (service worker + manifest)
npm run preview  # sirve dist/ localmente en http://localhost:4173
```

El build incluye chunking automático de Vite y el service worker de Workbox para capacidades offline.

## 10. pgAdmin (opcional)

Para inspeccionar la base de datos via UI:

```bash
make tools-up   # levanta pgAdmin en http://localhost:5050
```

Credenciales: `PGADMIN_EMAIL` y `PGADMIN_PASSWORD` del `.env` (por defecto `admin@pmcopilot.local` / `changeme`).
Servidor: host `postgres`, puerto `5432`, usuario y contraseña del `.env`.
