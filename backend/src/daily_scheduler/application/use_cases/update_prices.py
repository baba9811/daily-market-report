"""Use case: update prices for open recommendations."""

from __future__ import annotations

import logging
from datetime import date

from daily_scheduler.domain.entities.price import PriceSnapshot
from daily_scheduler.domain.ports.finance_provider import (
    FinanceProviderPort,
)
from daily_scheduler.domain.ports.price_repository import (
    PriceRepositoryPort,
)
from daily_scheduler.domain.ports.recommendation_repository import (
    RecommendationRepositoryPort,
)

logger = logging.getLogger(__name__)


class UpdatePrices:
    """Fetch current prices for open recommendations."""

    def __init__(
        self,
        rec_repo: RecommendationRepositoryPort,
        price_repo: PriceRepositoryPort,
        finance: FinanceProviderPort,
    ) -> None:
        self._rec_repo = rec_repo
        self._price_repo = price_repo
        self._finance = finance

    def execute(self) -> int:
        """Update prices and return count of updated recs."""
        open_recs = self._rec_repo.get_open()
        updated = 0
        today = date.today()

        for rec in open_recs:
            data = self._finance.fetch_price(rec.ticker)
            if data is None:
                continue

            rec.current_price = data["price"]
            self._rec_repo.update(rec)
            updated += 1

        # Save price snapshots
        tickers = {rec.ticker for rec in open_recs}
        self._save_snapshots(tickers, today)

        logger.info("Updated %d recommendation prices", updated)
        return updated

    def _save_snapshots(
        self, tickers: set[str], snapshot_date: date,
    ) -> None:
        for ticker in tickers:
            existing = self._price_repo.get_by_ticker_and_date(
                ticker, snapshot_date,
            )
            if existing:
                continue

            data = self._finance.fetch_price(ticker)
            if data is None:
                continue

            snapshot = PriceSnapshot(
                ticker=ticker,
                snapshot_date=snapshot_date,
                price=data["price"],
                open_price=data.get("open_price"),
                high=data.get("high"),
                low=data.get("low"),
                volume=data.get("volume"),
            )
            self._price_repo.save(snapshot)
