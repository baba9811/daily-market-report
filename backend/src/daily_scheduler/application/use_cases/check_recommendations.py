"""Use case: check if target/stop has been hit on open recs."""

from __future__ import annotations

import logging

from daily_scheduler import tz
from daily_scheduler.constants import (
    DAY_TRADE_EXPIRY_DAYS,
    SWING_TRADE_EXPIRY_DAYS,
)
from daily_scheduler.domain.ports.finance_provider import (
    FinanceProviderPort,
)
from daily_scheduler.domain.ports.recommendation_repository import (
    RecommendationRepositoryPort,
)

logger = logging.getLogger(__name__)


class CheckRecommendations:
    """Check open recommendations for expiry and target/stop hits."""

    def __init__(
        self,
        rec_repo: RecommendationRepositoryPort,
        finance: FinanceProviderPort,
    ) -> None:
        self._rec_repo = rec_repo
        self._finance = finance

    def execute(self) -> int:
        """Check all open recs. Returns number updated."""

        open_recs = self._rec_repo.get_open()
        updated = 0
        today = tz.today()

        for rec in open_recs:
            changed = False

            # Auto-expire DAY trades
            if (
                rec.timeframe == "DAY"
                and rec.created_at
                and (today - rec.created_at.date()).days >= DAY_TRADE_EXPIRY_DAYS
            ):
                rec.status = "EXPIRED"
                rec.closed_at = tz.now()
                changed = True
                logger.info(
                    "Expired DAY recommendation: %s",
                    rec.ticker,
                )

            # Auto-expire SWING trades
            elif rec.created_at:
                days_open = (today - rec.created_at.date()).days
                if rec.timeframe == "SWING" and days_open > SWING_TRADE_EXPIRY_DAYS:
                    rec.status = "EXPIRED"
                    rec.closed_at = tz.now()
                    changed = True
                    logger.info(
                        "Expired SWING recommendation (>14d): %s",
                        rec.ticker,
                    )

            if changed:
                self._rec_repo.update(rec)
                updated += 1
                continue

            # Fetch price and check target/stop
            data = self._finance.fetch_price(rec.ticker)
            if data is None:
                continue

            rec.current_price = data["price"]
            hit = self._check_hit(rec, data["price"])
            if hit:
                updated += 1

            self._rec_repo.update(rec)

        return updated

    def _check_hit(
        self,
        rec: object,
        price: float,
    ) -> bool:
        """Check if target or stop has been hit."""
        from daily_scheduler.domain.entities.recommendation import (
            Recommendation,
        )

        assert isinstance(rec, Recommendation)

        if rec.direction == "LONG":
            if price >= rec.target_price:
                rec.status = "TARGET_HIT"
                rec.closed_at = tz.now()
                rec.closed_price = price
                rec.pnl_percent = (price - rec.entry_price) / rec.entry_price * 100
                logger.info(
                    "TARGET HIT: %s at %.2f (%.1f%%)",
                    rec.ticker,
                    price,
                    rec.pnl_percent,
                )
                return True
            if price <= rec.stop_loss:
                rec.status = "STOP_HIT"
                rec.closed_at = tz.now()
                rec.closed_price = price
                rec.pnl_percent = (price - rec.entry_price) / rec.entry_price * 100
                logger.info(
                    "STOP HIT: %s at %.2f (%.1f%%)",
                    rec.ticker,
                    price,
                    rec.pnl_percent,
                )
                return True

        elif rec.direction == "SHORT":
            if price <= rec.target_price:
                rec.status = "TARGET_HIT"
                rec.closed_at = tz.now()
                rec.closed_price = price
                rec.pnl_percent = (rec.entry_price - price) / rec.entry_price * 100
                logger.info(
                    "TARGET HIT (SHORT): %s at %.2f (%.1f%%)",
                    rec.ticker,
                    price,
                    rec.pnl_percent,
                )
                return True
            if price >= rec.stop_loss:
                rec.status = "STOP_HIT"
                rec.closed_at = tz.now()
                rec.closed_price = price
                rec.pnl_percent = (rec.entry_price - price) / rec.entry_price * 100
                logger.info(
                    "STOP HIT (SHORT): %s at %.2f (%.1f%%)",
                    rec.ticker,
                    price,
                    rec.pnl_percent,
                )
                return True

        return False
