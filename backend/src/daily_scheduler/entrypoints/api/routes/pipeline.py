"""Pipeline router — manual trigger for report generation."""

from __future__ import annotations

import threading

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/pipeline", tags=["pipeline"],
)

_pipeline_status: dict[str, object] = {
    "running": False,
    "last_result": None,
}


@router.post("/run")
def trigger_pipeline() -> dict:
    """Trigger the daily report pipeline manually."""
    if _pipeline_status["running"]:
        return {
            "status": "already_running",
            "message": "Pipeline is already running.",
        }

    def run_in_background() -> None:
        from daily_scheduler.database import (
            get_session_factory,
        )
        from daily_scheduler.infrastructure.dependencies import (
            get_daily_pipeline,
        )

        _pipeline_status["running"] = True
        try:
            factory = get_session_factory()
            with factory() as session:
                pipeline = get_daily_pipeline(session)
                success = pipeline.execute()
                _pipeline_status["last_result"] = (
                    "success" if success else "failed"
                )
        except Exception as e:
            _pipeline_status["last_result"] = (
                f"error: {e}"
            )
        finally:
            _pipeline_status["running"] = False

    thread = threading.Thread(
        target=run_in_background, daemon=True,
    )
    thread.start()

    return {
        "status": "started",
        "message": "Pipeline started in background.",
    }


@router.get("/status")
def get_pipeline_status() -> dict:
    """Return current pipeline status."""
    return dict(_pipeline_status)
