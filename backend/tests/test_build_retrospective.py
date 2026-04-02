"""Tests for BuildRetrospective use case."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock

from daily_scheduler import tz
from daily_scheduler.application.use_cases.build_retrospective import (
    BuildRetrospective,
)
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
        "status": "TARGET_HIT",
        "created_at": tz.now() - timedelta(days=5),
        "closed_at": tz.now(),
        "closed_price": 112.0,
        "pnl_percent": 12.0,
        "sector": "Technology",
    }
    defaults.update(overrides)
    return Recommendation(**defaults)  # type: ignore[arg-type]


class TestBuildDailyContext:
    def test_no_past_data_returns_default_message(self):
        rec_repo = MagicMock()
        rec_repo.get_by_period.return_value = []

        builder = BuildRetrospective(rec_repo)
        context, retro = builder.build_daily_context(date(2026, 3, 17))

        assert "No past recommendation data" in context
        assert retro.report_date == date(2026, 3, 17)

    def test_with_recommendations_builds_context(self):
        rec_repo = MagicMock()
        recs = [
            _make_rec(ticker="AAPL", status="TARGET_HIT", pnl_percent=10.0),
            _make_rec(id=2, ticker="TSLA", status="STOP_HIT", pnl_percent=-5.0),
            _make_rec(id=3, ticker="GOOG", status="OPEN", pnl_percent=None),
        ]
        rec_repo.get_by_period.return_value = recs

        builder = BuildRetrospective(rec_repo)
        context, retro = builder.build_daily_context(date(2026, 3, 17))

        assert "Past Recommendation Performance" in context
        assert "Summary Statistics" in context
        assert "Total recommendations: 3" in context
        assert retro.targets_hit == 1
        assert retro.stops_hit == 1

    def test_context_includes_sector_performance(self):
        rec_repo = MagicMock()
        recs = [
            _make_rec(sector="Tech", status="TARGET_HIT", pnl_percent=10.0),
            _make_rec(id=2, sector="Finance", status="STOP_HIT", pnl_percent=-5.0),
        ]
        rec_repo.get_by_period.return_value = recs

        builder = BuildRetrospective(rec_repo)
        context, _ = builder.build_daily_context(date(2026, 3, 17))

        assert "Sector Performance" in context
        assert "Strategy Performance" in context

    def test_context_includes_recent_7day_table(self):
        rec_repo = MagicMock()
        now = tz.now()
        recs = [
            _make_rec(created_at=now - timedelta(days=2), status="OPEN", pnl_percent=None),
        ]
        rec_repo.get_by_period.return_value = recs

        builder = BuildRetrospective(rec_repo)
        context, _ = builder.build_daily_context()

        assert "Recent 7-Day Recommendations" in context
        assert "Apple" in context


class TestBuildWeeklyAnalysis:
    def test_no_recs_returns_none(self):
        rec_repo = MagicMock()
        rec_repo.get_by_period.return_value = []

        builder = BuildRetrospective(rec_repo)
        result = builder.build_weekly_analysis(date(2026, 3, 16))

        assert result is None

    def test_builds_weekly_analysis_with_data(self):
        rec_repo = MagicMock()
        monday = date(2026, 3, 16)
        # created_at must fall within the previous week (3/9 ~ 3/16)
        prev_week_date = tz.combine(monday - timedelta(days=4))
        recs = [
            _make_rec(
                ticker="AAPL",
                status="TARGET_HIT",
                pnl_percent=10.0,
                created_at=prev_week_date,
                sector="Tech",
            ),
            _make_rec(
                id=2,
                ticker="TSLA",
                status="STOP_HIT",
                pnl_percent=-5.0,
                created_at=prev_week_date,
                sector="Auto",
            ),
        ]
        rec_repo.get_by_period.return_value = recs

        builder = BuildRetrospective(rec_repo)
        result = builder.build_weekly_analysis(monday)

        assert result is not None
        assert result.win_count == 1
        assert result.loss_count == 1
        assert result.best_pick_ticker == "AAPL"
        assert result.worst_pick_ticker == "TSLA"


class TestWinRate:
    def test_empty_returns_zero(self):
        assert BuildRetrospective._win_rate([]) == 0.0

    def test_all_wins(self):
        recs = [
            _make_rec(status="TARGET_HIT"),
            _make_rec(id=2, status="TARGET_HIT"),
        ]
        assert BuildRetrospective._win_rate(recs) == 100.0

    def test_mixed(self):
        recs = [
            _make_rec(status="TARGET_HIT"),
            _make_rec(id=2, status="STOP_HIT"),
        ]
        assert BuildRetrospective._win_rate(recs) == 50.0


class TestClosedTradeRationales:
    def test_context_includes_closed_trade_rationales(self):
        rec_repo = MagicMock()
        now = tz.now()
        recs = [
            _make_rec(
                status="TARGET_HIT",
                pnl_percent=8.0,
                rationale="Strong AI demand + MACD bullish crossover",
                created_at=now - timedelta(days=2),
            ),
            _make_rec(
                id=2,
                ticker="TSLA",
                name="Tesla",
                status="STOP_HIT",
                pnl_percent=-3.0,
                rationale="EV sector recovery after oversold RSI",
                created_at=now - timedelta(days=3),
            ),
        ]
        rec_repo.get_by_period.return_value = recs

        builder = BuildRetrospective(rec_repo)
        context, _ = builder.build_daily_context()

        assert "Recently Closed Trades" in context
        assert "Original Rationale" in context
        assert "Strong AI demand" in context
        assert "EV sector recovery" in context

    def test_empty_rationale_shows_na(self):
        rec_repo = MagicMock()
        now = tz.now()
        recs = [
            _make_rec(
                status="STOP_HIT",
                pnl_percent=-2.0,
                rationale="",
                created_at=now - timedelta(days=1),
            ),
        ]
        rec_repo.get_by_period.return_value = recs

        builder = BuildRetrospective(rec_repo)
        context, _ = builder.build_daily_context()

        assert "N/A" in context

    def test_long_rationale_is_truncated(self):
        rec_repo = MagicMock()
        now = tz.now()
        long_rationale = "A" * 300
        recs = [
            _make_rec(
                status="TARGET_HIT",
                pnl_percent=5.0,
                rationale=long_rationale,
                created_at=now - timedelta(days=1),
            ),
        ]
        rec_repo.get_by_period.return_value = recs

        builder = BuildRetrospective(rec_repo)
        context, _ = builder.build_daily_context()

        assert "A" * 200 + "..." in context
        assert "A" * 300 not in context


class TestLessons:
    def test_low_sector_win_rate_warning(self):
        lines: list[str] = []
        sector_stats = {"BadSector": {"count": 5, "wins": 1, "losses": 4, "total_pnl": -20.0}}
        BuildRetrospective._add_lessons(lines, sector_stats, [], [], 0.0, 0.0)
        assert any("Warning" in line and "BadSector" in line for line in lines)

    def test_high_sector_win_rate_tip(self):
        lines: list[str] = []
        sector_stats = {"GoodSector": {"count": 5, "wins": 4, "losses": 1, "total_pnl": 30.0}}
        BuildRetrospective._add_lessons(lines, sector_stats, [], [], 0.0, 0.0)
        assert any("Tip" in line and "GoodSector" in line for line in lines)

    def test_swing_outperforms_day_tip(self):
        lines: list[str] = []
        day_recs = [_make_rec()]
        swing_recs = [_make_rec(id=2)]
        BuildRetrospective._add_lessons(lines, {}, day_recs, swing_recs, 30.0, 60.0)
        assert any("Swing" in line for line in lines)

    def test_macro_micro_reflection_always_present(self):
        lines: list[str] = []
        BuildRetrospective._add_lessons(lines, {}, [], [], 0.0, 0.0)
        assert any("macroeconomic" in line and "microeconomic" in line for line in lines)
