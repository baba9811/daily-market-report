"""FastAPI application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from daily_scheduler.routers import dashboard, performance, pipeline, reports, retrospective, settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Daily Scheduler",
        description="AI-powered daily news & trading report system",
        version="0.1.0",
    )

    # CORS for local frontend dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routers
    app.include_router(dashboard.router)
    app.include_router(reports.router)
    app.include_router(performance.router)
    app.include_router(retrospective.router)
    app.include_router(settings.router)
    app.include_router(pipeline.router)

    # Serve built frontend in production
    frontend_dist = Path(__file__).resolve().parents[4] / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    return app


app = create_app()
