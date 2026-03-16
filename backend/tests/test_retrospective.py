"""Tests for retrospective service."""

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from daily_scheduler.models.recommendation import Recommendation
from daily_scheduler.models.report import Report
from daily_scheduler.services.retrospective import build_daily_context


def _create_recommendation(
    db: Session,
    report_id: int,
    ticker: str = "AAPL",
    status: str = "OPEN",
    pnl: float | None = None,
    sector: str = "Technology",
    timeframe: str = "SWING",
    days_ago: int = 0,
) -> Recommendation:
    rec = Recommendation(
        report_id=report_id,
        ticker=ticker,
        name=f"Test {ticker}",
        market="NASDAQ",
        direction="LONG",
        timeframe=timeframe,
        entry_price=100.0,
        target_price=110.0,
        stop_loss=95.0,
        sector=sector,
        status=status,
        pnl_percent=pnl,
    )
    db.add(rec)
    db.flush()
    # Backdate created_at
    if days_ago > 0:
        rec.created_at = datetime.now() - timedelta(days=days_ago)
    db.commit()
    return rec


class TestBuildDailyContext:
    def test_no_data_returns_first_report_message(self, db: Session):
        context = build_daily_context(db, date.today())
        assert "No past recommendation data" in context

    def test_with_recommendations(self, db: Session):
        report = Report(report_date=date.today() - timedelta(days=1), report_type="daily")
        db.add(report)
        db.flush()

        _create_recommendation(db, report.id, "AAPL", "TARGET_HIT", 5.0, days_ago=2)
        _create_recommendation(db, report.id, "TSLA", "STOP_HIT", -3.0, days_ago=2)
        _create_recommendation(db, report.id, "GOOGL", "OPEN", days_ago=1)

        context = build_daily_context(db, date.today())

        assert "## Past Recommendation Performance" in context
        assert "### Summary Statistics" in context
        assert "Total recommendations: 3" in context
        assert "Target hit: 1" in context
        assert "Stop loss hit: 1" in context
        assert "Open: 1" in context

    def test_sector_performance_included(self, db: Session):
        report = Report(report_date=date.today() - timedelta(days=1), report_type="daily")
        db.add(report)
        db.flush()

        for i in range(4):
            _create_recommendation(
                db, report.id, f"T{i}", "TARGET_HIT", 3.0,
                sector="Technology", days_ago=2,
            )

        context = build_daily_context(db, date.today())
        assert "### Sector Performance" in context
        assert "Technology" in context

    def test_lessons_generated_for_low_win_rate(self, db: Session):
        report = Report(report_date=date.today() - timedelta(days=1), report_type="daily")
        db.add(report)
        db.flush()

        # 0 wins, 4 losses in "Biotech"
        for i in range(4):
            _create_recommendation(
                db, report.id, f"BIO{i}", "STOP_HIT", -2.0,
                sector="Biotech", days_ago=2,
            )

        context = build_daily_context(db, date.today())
        assert "Warning" in context
        assert "Biotech" in context
