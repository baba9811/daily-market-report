"""Tests for UpdatePrices use case."""

from __future__ import annotations

from unittest.mock import MagicMock

from daily_scheduler import tz
from daily_scheduler.application.use_cases.update_prices import UpdatePrices
from daily_scheduler.domain.entities.recommendation import Recommendation


def _make_rec(**overrides: object) -> Recommendation:
    defaults: dict[str, object] = {
        "id": 1,
        "report_id": 1,
        "ticker": "AAPL",
        "name": "Apple",
        "market": "NASDAQ",
        "direction": "LONG",
        "timeframe": "SWING",
        "entry_price": 100.0,
        "target_price": 110.0,
        "stop_loss": 90.0,
        "status": "OPEN",
        "created_at": tz.now(),
    }
    defaults.update(overrides)
    return Recommendation(**defaults)  # type: ignore[arg-type]


class TestUpdatePrices:
    def test_updates_price_on_recommendation(self):
        rec_repo = MagicMock()
        price_repo = MagicMock()
        finance = MagicMock()

        rec = _make_rec(ticker="AAPL")
        rec_repo.get_open.return_value = [rec]
        finance.fetch_price.return_value = {
            "price": 155.0,
            "open_price": 153.0,
            "high": 156.0,
            "low": 152.0,
            "volume": 1000000,
        }
        price_repo.get_by_ticker_and_date.return_value = None

        updater = UpdatePrices(rec_repo, price_repo, finance)
        updated = updater.execute()

        assert updated == 1
        assert rec.current_price == 155.0
        rec_repo.update.assert_called_once_with(rec)
        price_repo.save.assert_called_once()

    def test_skips_when_price_fetch_fails(self):
        rec_repo = MagicMock()
        price_repo = MagicMock()
        finance = MagicMock()

        rec = _make_rec()
        rec_repo.get_open.return_value = [rec]
        finance.fetch_price.return_value = None

        updater = UpdatePrices(rec_repo, price_repo, finance)
        updated = updater.execute()

        assert updated == 0
        rec_repo.update.assert_not_called()

    def test_no_open_recs_returns_zero(self):
        rec_repo = MagicMock()
        price_repo = MagicMock()
        finance = MagicMock()
        rec_repo.get_open.return_value = []

        updater = UpdatePrices(rec_repo, price_repo, finance)
        updated = updater.execute()

        assert updated == 0
        finance.fetch_price.assert_not_called()

    def test_skips_snapshot_if_already_exists(self):
        rec_repo = MagicMock()
        price_repo = MagicMock()
        finance = MagicMock()

        rec = _make_rec(ticker="AAPL")
        rec_repo.get_open.return_value = [rec]
        finance.fetch_price.return_value = {"price": 155.0}
        price_repo.get_by_ticker_and_date.return_value = MagicMock()

        updater = UpdatePrices(rec_repo, price_repo, finance)
        updater.execute()

        price_repo.save.assert_not_called()

    def test_multiple_recs_updated(self):
        rec_repo = MagicMock()
        price_repo = MagicMock()
        finance = MagicMock()

        rec1 = _make_rec(id=1, ticker="AAPL")
        rec2 = _make_rec(id=2, ticker="TSLA")
        rec_repo.get_open.return_value = [rec1, rec2]
        finance.fetch_price.side_effect = [
            {"price": 155.0},
            {"price": 250.0},
            {"price": 155.0},
            {"price": 250.0},
        ]
        price_repo.get_by_ticker_and_date.return_value = None

        updater = UpdatePrices(rec_repo, price_repo, finance)
        updated = updater.execute()

        assert updated == 2
        assert rec1.current_price == 155.0
        assert rec2.current_price == 250.0
