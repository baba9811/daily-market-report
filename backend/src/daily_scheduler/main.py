"""FastAPI application factory — delegates to entrypoints."""

from __future__ import annotations

from daily_scheduler.entrypoints.api.app import create_app

app = create_app()
