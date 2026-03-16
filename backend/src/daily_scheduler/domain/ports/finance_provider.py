"""Port: finance data provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class FinanceProviderPort(ABC):
    """Abstract interface for fetching stock prices."""

    @abstractmethod
    def fetch_price(self, ticker: str) -> dict | None:
        """Fetch latest price data for a ticker.

        Returns dict with keys: price, open_price, high, low, volume.
        Returns None on failure.
        """
        ...
