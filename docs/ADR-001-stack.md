# ADR-001 — Stack Tecnológico

**Estado**: Aceptado  
**Fecha**: 2026-04-24  
**Autor**: Marcos Vese  

---

## Contexto

PM Copilot es un proyecto de desarrollo en solitario con apoyo de IA que debe equilibrar velocidad de desarrollo, mantenibilidad a largo plazo y capacidad de demostrar patrones de ingeniería modernos. El stack debe soportar:

- Backend con lógica compleja de orquestación LLM y RAG
- Integraciones con múltiples APIs externas (Confluence, Jira, GitHub, Anthropic, Ollama)
- Frontend conversacional con streaming de respuestas
- Despliegue sencillo con presupuesto limitado
- Código accesible para documentar y compartir como metodología

---

## Decisión

### Backend: Python 3.12 + FastAPI

**Elegido sobre**: Node.js/Express, Go, Django

**Razones**:
- Python es el lenguaje dominante en el ecosistema LLM/ML — acceso a todas las bibliotecas relevantes (`anthropic`, `chromadb`, `langchain`, `sentence-transformers`)
- FastAPI ofrece tipado nativo con Pydantic, async nativo, documentación OpenAPI automática y rendimiento adecuado para el caso de uso
- Menor fricción para el desarrollador en comparación con tipado explícito de Go o ecosistema fragmentado de Node para IA
- Excelente soporte de la comunidad IA para Python

### Base de Datos: PostgreSQL

**Elegido sobre**: SQLite, MongoDB, MySQL

**Razones**:
- Estándar de facto para aplicaciones Python con SQLAlchemy
- Railway ofrece PostgreSQL gestionado en su tier gratuito
- Soporte para JSONB útil para metadatos flexibles de tareas y estimaciones
- Herramientas de migración maduras con Alembic

### Vector Store: ChromaDB

**Elegido sobre**: Pinecone, Weaviate, pgvector, Qdrant

**Razones**:
- Open source, self-hosted sin coste operativo de API
- Fácil de ejecutar localmente con Docker para desarrollo
- API Python sencilla con buen soporte para metadata filtering
- Desplegable en Railway como contenedor
- Suficiente para la escala prevista (< 100k documentos en MVP)

### Embeddings: nomic-embed-text via Ollama

**Elegido sobre**: OpenAI `text-embedding-ada-002`, sentence-transformers local

**Razones**:
- Completamente local — sin costes por token ni dependencia de API externa para embeddings
- `nomic-embed-text` ofrece calidad de embeddings comparable a OpenAI en benchmarks MTEB
- Ollama gestiona la descarga y ejecución del modelo
- Coherente con el objetivo de minimizar coste y dependencias externas para desarrollo

### LLM: Claude Sonnet/Haiku (Anthropic) + Ollama/llama3

**Elegido sobre**: GPT-4 (OpenAI), Gemini, solo Ollama

**Razones**:
- Claude Sonnet es el mejor modelo general para tareas de razonamiento y generación de código/documentos en 2025
- Claude Haiku para tareas que requieren velocidad (routing rápido, clasificaciones)
- Ollama/llama3 como fallback y para desarrollo local — reduce costes durante iteración
- El diseño de LLM Router permite añadir o sustituir proveedores sin cambiar la lógica de negocio

### Frontend: React 18 + TypeScript + Vite

**Elegido sobre**: Vue.js, Svelte, Next.js, Angular

**Razones**:
- React es el framework de mayor adopción con mayor ecosistema de componentes
- TypeScript reduce bugs en el cliente y mejora la experiencia de desarrollo
- Vite ofrece HMR instantáneo y build optimizado
- Sin SSR necesario en MVP — React SPA suficiente, evita complejidad de Next.js
- Amplio ecosistema de componentes de UI (shadcn/ui, Radix, etc.)

### Hosting: Vercel (frontend) + Railway (backend)

**Elegido sobre**: AWS, GCP, Heroku, Render, Fly.io

**Razones**:
- Vercel: despliegue automático de frontend desde GitHub, CDN global, tier gratuito generoso
- Railway: el más sencillo para desplegar FastAPI + PostgreSQL + contenedores adicionales (ChromaDB) sin configuración de infraestructura compleja
- Ambos tienen integración directa con GitHub para CI/CD

---

## Consecuencias

### Positivas
- Stack coherente y maduro con excelente soporte de comunidad
- Coste mínimo en desarrollo (Ollama gratuito, Railway/Vercel tiers gratuitos)
- Máxima flexibilidad en capa LLM gracias al Router
- Python facilita iterar rápido con LLMs y RAG

### Negativas / Trade-offs
- Python tiene mayor consumo de memoria que Go o Rust para el backend
- ChromaDB auto-hosted requiere gestión propia de backups y escalado futuro
- Sin SSR implica peor SEO (no relevante para una app de gestión de proyectos)
- Ollama requiere hardware local suficiente (≥ 16GB RAM recomendado)

### Deuda Técnica Aceptada
- Si el proyecto escala, considerar migración de ChromaDB a Qdrant Cloud o pgvector para simplificar operaciones
- Si el presupuesto lo permite, evaluar OpenAI embeddings vs nomic-embed-text con benchmark formal
