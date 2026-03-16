"""Retrospective router — weekly analyses and daily checks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from daily_scheduler.database import get_db
from daily_scheduler.models.retrospective import Retrospective, WeeklyAnalysis

router = APIRouter(prefix="/api/retrospective", tags=["retrospective"])


@router.get("/weekly")
def list_weekly_analyses(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    analyses = (
        db.query(WeeklyAnalysis)
        .order_by(WeeklyAnalysis.week_start.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return [
        {
            "id": a.id,
            "week_start": a.week_start.isoformat(),
            "week_end": a.week_end.isoformat(),
            "total_recommendations": a.total_recommendations,
            "win_count": a.win_count,
            "loss_count": a.loss_count,
            "avg_return_pct": a.avg_return_pct,
            "best_pick_ticker": a.best_pick_ticker,
            "worst_pick_ticker": a.worst_pick_ticker,
            "analysis_text": a.analysis_text,
        }
        for a in analyses
    ]


@router.get("/weekly/{analysis_id}")
def get_weekly_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(WeeklyAnalysis).filter(WeeklyAnalysis.id == analysis_id).first()
    if not analysis:
        return {"error": "Not found"}
    return {
        "id": analysis.id,
        "week_start": analysis.week_start.isoformat(),
        "week_end": analysis.week_end.isoformat(),
        "total_recommendations": analysis.total_recommendations,
        "win_count": analysis.win_count,
        "loss_count": analysis.loss_count,
        "avg_return_pct": analysis.avg_return_pct,
        "best_pick_ticker": analysis.best_pick_ticker,
        "worst_pick_ticker": analysis.worst_pick_ticker,
        "sector_breakdown": analysis.sector_breakdown,
        "analysis_text": analysis.analysis_text,
        "lessons": analysis.lessons,
    }


@router.get("/daily-checks")
def list_daily_checks(
    limit: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db),
):
    checks = (
        db.query(Retrospective)
        .order_by(Retrospective.report_date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": c.id,
            "report_date": c.report_date.isoformat(),
            "recommendations_checked": c.recommendations_checked,
            "targets_hit": c.targets_hit,
            "stops_hit": c.stops_hit,
            "expired_count": c.expired_count,
        }
        for c in checks
    ]
