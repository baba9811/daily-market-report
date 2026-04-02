"""Tests for SQLAlchemyRetrospectiveRepository."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from daily_scheduler.domain.entities.retrospective import (
    Retrospective,
    WeeklyAnalysis,
)
from daily_scheduler.infrastructure.adapters.persistence.retrospective_repository import (
    SQLAlchemyRetrospectiveRepository,
)


class TestRetrospectiveRepository:
    def test_save_and_retrieve(self, db: Session):
        repo = SQLAlchemyRetrospectiveRepository(db)
        retro = Retrospective(
            report_date=date(2026, 3, 17),
            recommendations_checked=10,
            targets_hit=3,
            stops_hit=2,
            expired_count=1,
            context_block="test context",
        )
        saved = repo.save(retro)
        db.commit()

        assert saved.id is not None
        assert saved.targets_hit == 3

    def test_save_upserts_on_same_date(self, db: Session):
        repo = SQLAlchemyRetrospectiveRepository(db)
        retro1 = Retrospective(
            report_date=date(2026, 3, 17),
            targets_hit=3,
            stops_hit=2,
        )
        repo.save(retro1)
        db.commit()

        retro2 = Retrospective(
            report_date=date(2026, 3, 17),
            targets_hit=5,
            stops_hit=4,
        )
        updated = repo.save(retro2)
        db.commit()

        assert updated.targets_hit == 5
        assert updated.stops_hit == 4


class TestWeeklyAnalysisRepository:
    def test_save_weekly(self, db: Session):
        repo = SQLAlchemyRetrospectiveRepository(db)
        analysis = WeeklyAnalysis(
            week_start=date(2026, 3, 10),
            week_end=date(2026, 3, 16),
            total_recommendations=8,
            win_count=5,
            loss_count=3,
            avg_return_pct=2.5,
            best_pick_ticker="AAPL",
            worst_pick_ticker="TSLA",
        )
        saved = repo.save_weekly(analysis)
        db.commit()

        assert saved.id is not None
        assert saved.win_count == 5

    def test_save_weekly_upserts_on_same_week(self, db: Session):
        repo = SQLAlchemyRetrospectiveRepository(db)
        a1 = WeeklyAnalysis(
            week_start=date(2026, 3, 10),
            week_end=date(2026, 3, 16),
            win_count=3,
            loss_count=2,
        )
        repo.save_weekly(a1)
        db.commit()

        a2 = WeeklyAnalysis(
            week_start=date(2026, 3, 10),
            week_end=date(2026, 3, 16),
            win_count=6,
            loss_count=1,
        )
        updated = repo.save_weekly(a2)
        db.commit()

        assert updated.win_count == 6
        assert updated.loss_count == 1
