"""Port: retrospective persistence interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from daily_scheduler.domain.entities.retrospective import (
    Retrospective,
    WeeklyAnalysis,
)


class RetrospectiveRepositoryPort(ABC):
    """Abstract interface for retrospective persistence."""

    @abstractmethod
    def save(self, retrospective: Retrospective) -> Retrospective:
        """Persist a daily retrospective check."""

    @abstractmethod
    def save_weekly(self, analysis: WeeklyAnalysis) -> WeeklyAnalysis:
        """Persist a weekly analysis."""
