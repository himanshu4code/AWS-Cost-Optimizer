"""FastAPI application factory and router registration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.apis.auth import router as auth_router
from api.apis.core import router as core_router
from api.apis.scans import router as scans_router
from api.config.settings import get_settings, get_frontend_origins


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_frontend_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(core_router)
    app.include_router(auth_router)
    app.include_router(scans_router)
    return app


app = create_app()
