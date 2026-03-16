"""Retrospective and WeeklyAnalysis entities — pure Python dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Retrospective:
    """Daily performance check snapshot."""

    report_date: date
    recommendations_checked: int = 0
    targets_hit: int = 0
    stops_hit: int = 0
    expired_count: int = 0
    context_block: str = ""
    id: int | None = None
    created_at: datetime | None = field(default=None)


@dataclass
class WeeklyAnalysis:
    """Comprehensive weekly performance analysis."""

    week_start: date
    week_end: date
    total_recommendations: int = 0
    win_count: int = 0
    loss_count: int = 0
    avg_return_pct: float | None = None
    best_pick_ticker: str = ""
    worst_pick_ticker: str = ""
    sector_breakdown: str = "{}"  # JSON
    analysis_text: str = ""
    lessons: str = "[]"  # JSON array
    id: int | None = None
    created_at: datetime | None = field(default=None)
