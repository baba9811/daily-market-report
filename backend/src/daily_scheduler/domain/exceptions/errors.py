"""Domain-specific exceptions."""

from __future__ import annotations


class DomainError(Exception):
    """Base exception for all domain errors."""


class ReportNotFoundError(DomainError):
    """Raised when a report is not found."""


class ReportAlreadyExistsError(DomainError):
    """Raised when a report already exists for a given date."""


class GenerationError(DomainError):
    """Raised when report generation fails."""


class PipelineError(DomainError):
    """Raised when the pipeline encounters an error."""
