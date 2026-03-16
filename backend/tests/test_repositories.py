"""Tests for SQLAlchemy repository implementations."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from daily_scheduler import tz
from daily_scheduler.domain.entities.price import PriceSnapshot
from daily_scheduler.domain.entities.recommendation import Recommendation
from daily_scheduler.domain.entities.report import Report
from daily_scheduler.infrastructure.adapters.persistence.price_repository import (
    SQLAlchemyPriceRepository,
)
from daily_scheduler.infrastructure.adapters.persistence.recommendation_repository import (
    SQLAlchemyRecommendationRepository,
)
from daily_scheduler.infrastructure.adapters.persistence.report_repository import (
    SQLAlchemyReportRepository,
)


class TestReportRepository:
    def test_save_and_get_by_id(self, db: Session):
        repo = SQLAlchemyReportRepository(db)
        report = Report(
            report_date=date(2026, 3, 17),
            report_type="daily",
            html_content="<html>test</html>",
            summary="Test",
        )
        saved = repo.save(report)
        db.commit()

        assert saved.id is not None
        fetched = repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.summary == "Test"

    def test_get_by_date(self, db: Session):
        repo = SQLAlchemyReportRepository(db)
        report = Report(
            report_date=date(2026, 3, 17),
            report_type="daily",
        )
        repo.save(report)
        db.commit()

        fetched = repo.get_by_date(date(2026, 3, 17), "daily")
        assert fetched is not None

        missing = repo.get_by_date(date(2026, 3, 18), "daily")
        assert missing is None

    def test_get_latest(self, db: Session):
        repo = SQLAlchemyReportRepository(db)
        repo.save(Report(report_date=date(2026, 3, 17), report_type="daily"))

        latest = repo.get_latest("daily")
        assert latest is not None
        assert latest.report_date == date(2026, 3, 17)

    def test_get_latest_returns_none_when_empty(self, db: Session):
        repo = SQLAlchemyReportRepository(db)
        assert repo.get_latest("daily") is None

    def test_list_reports_pagination(self, db: Session):
        repo = SQLAlchemyReportRepository(db)
        for i in range(5):
            repo.save(Report(report_date=date(2026, 3, 10 + i), report_type="daily"))
        db.commit()

        page1 = repo.list_reports(per_page=2, page=1)
        assert len(page1) == 2

        page2 = repo.list_reports(per_page=2, page=2)
        assert len(page2) == 2

    def test_list_reports_filter_by_type(self, db: Session):
        repo = SQLAlchemyReportRepository(db)
        repo.save(Report(report_date=date(2026, 3, 17), report_type="daily"))
        repo.save(Report(report_date=date(2026, 3, 17), report_type="weekly"))
        db.commit()

        daily = repo.list_reports(report_type="daily")
        assert len(daily) == 1

        all_reports = repo.list_reports(report_type="all")
        assert len(all_reports) == 2

    def test_get_by_id_returns_none_for_missing(self, db: Session):
        repo = SQLAlchemyReportRepository(db)
        assert repo.get_by_id(999) is None


class TestRecommendationRepository:
    def _save_report(self, db: Session) -> int:
        repo = SQLAlchemyReportRepository(db)
        saved = repo.save(Report(report_date=date(2026, 3, 17), report_type="daily"))
        db.flush()
        assert saved.id is not None
        return saved.id

    def test_save_and_get_open(self, db: Session):
        report_id = self._save_report(db)
        repo = SQLAlchemyRecommendationRepository(db)
        rec = Recommendation(
            report_id=report_id,
            ticker="AAPL",
            name="Apple",
            market="NASDAQ",
            direction="LONG",
            timeframe="SWING",
            entry_price=185.0,
            target_price=195.0,
            stop_loss=180.0,
        )
        repo.save(rec)
        db.commit()

        open_recs = repo.get_open()
        assert len(open_recs) == 1
        assert open_recs[0].ticker == "AAPL"

    def test_save_many(self, db: Session):
        report_id = self._save_report(db)
        repo = SQLAlchemyRecommendationRepository(db)
        recs = [
            Recommendation(
                report_id=report_id,
                ticker="AAPL",
                name="Apple",
                market="NASDAQ",
                direction="LONG",
                timeframe="SWING",
                entry_price=185.0,
                target_price=195.0,
                stop_loss=180.0,
            ),
            Recommendation(
                report_id=report_id,
                ticker="TSLA",
                name="Tesla",
                market="NASDAQ",
                direction="SHORT",
                timeframe="DAY",
                entry_price=250.0,
                target_price=230.0,
                stop_loss=260.0,
            ),
        ]
        saved = repo.save_many(recs)
        db.commit()

        assert len(saved) == 2
        all_recs = repo.list_all()
        assert len(all_recs) == 2

    def test_update_recommendation(self, db: Session):
        report_id = self._save_report(db)
        repo = SQLAlchemyRecommendationRepository(db)
        rec = Recommendation(
            report_id=report_id,
            ticker="AAPL",
            name="Apple",
            market="NASDAQ",
            direction="LONG",
            timeframe="SWING",
            entry_price=185.0,
            target_price=195.0,
            stop_loss=180.0,
        )
        saved = repo.save(rec)
        db.commit()

        saved.status = "TARGET_HIT"
        saved.closed_price = 196.0
        saved.pnl_percent = 5.95
        saved.closed_at = tz.now()
        repo.update(saved)
        db.commit()

        open_recs = repo.get_open()
        assert len(open_recs) == 0

    def test_get_by_period(self, db: Session):
        report_id = self._save_report(db)
        repo = SQLAlchemyRecommendationRepository(db)
        rec = Recommendation(
            report_id=report_id,
            ticker="AAPL",
            name="Apple",
            market="NASDAQ",
            direction="LONG",
            timeframe="SWING",
            entry_price=185.0,
            target_price=195.0,
            stop_loss=180.0,
        )
        repo.save(rec)
        db.commit()

        since = tz.now() - timedelta(days=30)
        recs = repo.get_by_period(since)
        assert len(recs) >= 1

    def test_list_all_with_status_filter(self, db: Session):
        report_id = self._save_report(db)
        repo = SQLAlchemyRecommendationRepository(db)
        rec1 = Recommendation(
            report_id=report_id,
            ticker="AAPL",
            name="Apple",
            market="NASDAQ",
            direction="LONG",
            timeframe="SWING",
            entry_price=185.0,
            target_price=195.0,
            stop_loss=180.0,
            status="OPEN",
        )
        rec2 = Recommendation(
            report_id=report_id,
            ticker="TSLA",
            name="Tesla",
            market="NASDAQ",
            direction="LONG",
            timeframe="DAY",
            entry_price=250.0,
            target_price=260.0,
            stop_loss=245.0,
            status="TARGET_HIT",
        )
        repo.save_many([rec1, rec2])
        db.commit()

        open_only = repo.list_all(status="OPEN")
        assert len(open_only) == 1
        assert open_only[0].ticker == "AAPL"


class TestPriceRepository:
    def test_save_and_get(self, db: Session):
        repo = SQLAlchemyPriceRepository(db)
        snapshot = PriceSnapshot(
            ticker="AAPL",
            snapshot_date=date(2026, 3, 17),
            price=185.50,
            open_price=184.0,
            high=186.0,
            low=183.0,
            volume=50000000,
        )
        saved = repo.save(snapshot)
        db.commit()

        assert saved.id is not None
        fetched = repo.get_by_ticker_and_date("AAPL", date(2026, 3, 17))
        assert fetched is not None
        assert fetched.price == 185.50

    def test_returns_none_for_missing(self, db: Session):
        repo = SQLAlchemyPriceRepository(db)
        result = repo.get_by_ticker_and_date("AAPL", date(2026, 1, 1))
        assert result is None
