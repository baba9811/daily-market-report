"""Pipeline router — manual trigger for report generation."""

from __future__ import annotations

import threading

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/pipeline",
    tags=["pipeline"],
)

_lock = threading.Lock()


class PipelineStatusOut(BaseModel):
    """Current pipeline status."""

    running: bool
    last_result: str | None


class _PipelineState:
    """Thread-safe mutable pipeline state."""

    def __init__(self) -> None:
        self.running = False
        self.last_result: str | None = None


_state = _PipelineState()


class PipelineRunResult(BaseModel):
    """Result of pipeline trigger."""

    status: str
    message: str


@router.post("/run", response_model=PipelineRunResult)
def trigger_pipeline() -> PipelineRunResult:
    """Trigger the daily report pipeline manually."""
    with _lock:
        if _state.running:
            return PipelineRunResult(
                status="already_running",
                message="Pipeline is already running.",
            )
        _state.running = True

    def run_in_background() -> None:
        from daily_scheduler.database import (
            get_session_factory,
        )
        from daily_scheduler.infrastructure.dependencies import (
            get_daily_pipeline,
        )

        try:
            factory = get_session_factory()
            session = factory()
            try:
                pipeline = get_daily_pipeline(session)
                success = pipeline.execute()
                result = "success" if success else "failed"
                session.commit()
            except Exception as e:  # pylint: disable=broad-exception-caught
                session.rollback()
                result = f"error: {e}"
            finally:
                session.close()
        except Exception as e:  # pylint: disable=broad-exception-caught
            result = f"error: {e}"

        with _lock:
            _state.running = False
            _state.last_result = result

    thread = threading.Thread(
        target=run_in_background,
        daemon=True,
    )
    thread.start()

    return PipelineRunResult(
        status="started",
        message="Pipeline started in background.",
    )


@router.get("/status", response_model=PipelineStatusOut)
def get_pipeline_status() -> PipelineStatusOut:
    """Return current pipeline status."""
    with _lock:
        return PipelineStatusOut(
            running=_state.running,
            last_result=_state.last_result,
        )
