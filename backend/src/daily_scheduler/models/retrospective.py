"""Retrospective and WeeklyAnalysis models — performance tracking."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from daily_scheduler.database import Base


class Retrospective(Base):
    __tablename__ = "retrospectives"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    recommendations_checked: Mapped[int] = mapped_column(Integer, default=0)
    targets_hit: Mapped[int] = mapped_column(Integer, default=0)
    stops_hit: Mapped[int] = mapped_column(Integer, default=0)
    expired_count: Mapped[int] = mapped_column(Integer, default=0)
    context_block: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class WeeklyAnalysis(Base):
    __tablename__ = "weekly_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)
    total_recommendations: Mapped[int] = mapped_column(Integer, default=0)
    win_count: Mapped[int] = mapped_column(Integer, default=0)
    loss_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_return_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_pick_ticker: Mapped[str] = mapped_column(default="")
    worst_pick_ticker: Mapped[str] = mapped_column(default="")
    sector_breakdown: Mapped[str] = mapped_column(Text, default="{}")  # JSON
    analysis_text: Mapped[str] = mapped_column(Text, default="")
    lessons: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
