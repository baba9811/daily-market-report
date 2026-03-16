"""Port: recommendation persistence interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from daily_scheduler.domain.entities.recommendation import (
    Recommendation,
)


class RecommendationRepositoryPort(ABC):
    """Abstract interface for recommendation persistence."""

    @abstractmethod
    def get_open(self) -> list[Recommendation]:
        """Return all open recommendations."""

    @abstractmethod
    def get_by_period(
        self,
        since: datetime,
    ) -> list[Recommendation]:
        """Return recommendations created since the given datetime."""

    @abstractmethod
    def get_closed_by_period(
        self,
        since: datetime,
    ) -> list[Recommendation]:
        """Return closed recommendations since the given datetime."""

    @abstractmethod
    def save(self, rec: Recommendation) -> Recommendation:
        """Persist a single recommendation."""

    @abstractmethod
    def save_many(
        self,
        recs: list[Recommendation],
    ) -> list[Recommendation]:
        """Persist multiple recommendations."""

    @abstractmethod
    def update(self, rec: Recommendation) -> None:
        """Update an existing recommendation."""

    @abstractmethod
    def list_all(
        self,
        status: str = "all",
        limit: int = 100,
    ) -> list[Recommendation]:
        """List recommendations filtered by status."""
