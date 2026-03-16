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
    def get_open(self) -> list[Recommendation]: ...

    @abstractmethod
    def get_by_period(
        self,
        since: datetime,
    ) -> list[Recommendation]: ...

    @abstractmethod
    def get_closed_by_period(
        self,
        since: datetime,
    ) -> list[Recommendation]: ...

    @abstractmethod
    def save(self, rec: Recommendation) -> Recommendation: ...

    @abstractmethod
    def save_many(
        self,
        recs: list[Recommendation],
    ) -> list[Recommendation]: ...

    @abstractmethod
    def update(self, rec: Recommendation) -> None: ...

    @abstractmethod
    def list_all(
        self,
        status: str = "all",
        limit: int = 100,
    ) -> list[Recommendation]: ...
