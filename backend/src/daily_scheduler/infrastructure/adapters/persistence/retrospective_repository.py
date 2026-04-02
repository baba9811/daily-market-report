"""SQLAlchemy implementation of RetrospectiveRepositoryPort."""

from __future__ import annotations

from sqlalchemy.orm import Session

from daily_scheduler.domain.entities.retrospective import (
    Retrospective,
    WeeklyAnalysis,
)
from daily_scheduler.domain.ports.retrospective_repository import (
    RetrospectiveRepositoryPort,
)
from daily_scheduler.infrastructure.adapters.persistence.models import (
    RetrospectiveModel,
    WeeklyAnalysisModel,
)


class SQLAlchemyRetrospectiveRepository(RetrospectiveRepositoryPort):
    """Persist retrospective data via SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, retrospective: Retrospective) -> Retrospective:
        existing = (
            self._db.query(RetrospectiveModel)
            .filter(RetrospectiveModel.report_date == retrospective.report_date)
            .first()
        )
        if existing:
            existing.recommendations_checked = retrospective.recommendations_checked
            existing.targets_hit = retrospective.targets_hit
            existing.stops_hit = retrospective.stops_hit
            existing.expired_count = retrospective.expired_count
            existing.context_block = retrospective.context_block
            self._db.flush()
            return existing.to_entity()

        model = RetrospectiveModel.from_entity(retrospective)
        self._db.add(model)
        self._db.flush()
        return model.to_entity()

    def save_weekly(self, analysis: WeeklyAnalysis) -> WeeklyAnalysis:
        existing = (
            self._db.query(WeeklyAnalysisModel)
            .filter(WeeklyAnalysisModel.week_start == analysis.week_start)
            .first()
        )
        if existing:
            existing.total_recommendations = analysis.total_recommendations
            existing.win_count = analysis.win_count
            existing.loss_count = analysis.loss_count
            existing.avg_return_pct = analysis.avg_return_pct
            existing.best_pick_ticker = analysis.best_pick_ticker
            existing.worst_pick_ticker = analysis.worst_pick_ticker
            existing.sector_breakdown = analysis.sector_breakdown
            existing.analysis_text = analysis.analysis_text
            existing.lessons = analysis.lessons
            self._db.flush()
            return existing.to_entity()

        model = WeeklyAnalysisModel.from_entity(analysis)
        self._db.add(model)
        self._db.flush()
        return model.to_entity()
