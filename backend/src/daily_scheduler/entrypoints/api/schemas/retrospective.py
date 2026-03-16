"""Retrospective API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class WeeklyAnalysisOut(BaseModel):
    """Weekly analysis summary."""

    id: int
    week_start: str
    week_end: str
    total_recommendations: int
    win_count: int
    loss_count: int
    avg_return_pct: float | None
    best_pick_ticker: str | None
    worst_pick_ticker: str | None
    analysis_text: str | None


class WeeklyAnalysisDetailOut(WeeklyAnalysisOut):
    """Weekly analysis with full detail."""

    sector_breakdown: str | None
    lessons: str | None


class DailyCheckOut(BaseModel):
    """Daily retrospective check."""

    id: int
    report_date: str
    recommendations_checked: int
    targets_hit: int
    stops_hit: int
    expired_count: int
