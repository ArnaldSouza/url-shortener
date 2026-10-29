from fastapi import FastAPI

from app.api import health, links, redirect, stats
from app.config import settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(health.router)
    app.include_router(links.router)
    app.include_router(stats.router)
    app.include_router(redirect.router)  # must be last: catch-all route
    return app


app = create_app()
