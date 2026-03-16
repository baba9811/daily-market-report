"""Port: price snapshot persistence interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from daily_scheduler.domain.entities.price import PriceSnapshot


class PriceRepositoryPort(ABC):
    """Abstract interface for price snapshot persistence."""

    @abstractmethod
    def get_by_ticker_and_date(
        self,
        ticker: str,
        snapshot_date: date,
    ) -> PriceSnapshot | None:
        """Return a price snapshot for the given ticker and date."""

    @abstractmethod
    def save(self, snapshot: PriceSnapshot) -> PriceSnapshot:
        """Persist a price snapshot."""
