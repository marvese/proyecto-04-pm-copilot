from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import settings
from ..adapters.primary.api.auth_router import router as auth_router
from ..adapters.primary.api.projects_router import router as projects_router
from ..adapters.primary.api.tasks_router import router as tasks_router
from ..adapters.primary.api.chat_router import router as chat_router
from ..adapters.primary.api.estimate_router import router as estimate_router
from ..adapters.primary.api.reports_router import router as reports_router
from ..adapters.primary.api.knowledge_router import router as knowledge_router
from ..adapters.primary.api.sprints_router import router as sprints_router
from ..adapters.primary.websocket.chat_ws_handler import router as ws_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: restrict to frontend domain in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(tasks_router)
    app.include_router(chat_router)
    app.include_router(estimate_router)
    app.include_router(reports_router)
    app.include_router(knowledge_router)
    app.include_router(sprints_router)
    app.include_router(ws_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
