"""Domain exceptions."""

from __future__ import annotations

from daily_scheduler.domain.exceptions.errors import (
    DomainError,
    GenerationError,
    PipelineError,
    ReportAlreadyExistsError,
    ReportNotFoundError,
)

__all__ = [
    "DomainError",
    "GenerationError",
    "PipelineError",
    "ReportAlreadyExistsError",
    "ReportNotFoundError",
]
