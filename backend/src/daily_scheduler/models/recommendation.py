"""Recommendation model — individual stock picks from reports."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from daily_scheduler.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(Integer, ForeignKey("reports.id"), nullable=False)
    ticker: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    market: Mapped[str] = mapped_column(nullable=False)  # KOSPI, KOSDAQ, NYSE, NASDAQ
    direction: Mapped[str] = mapped_column(nullable=False)  # LONG, SHORT
    timeframe: Mapped[str] = mapped_column(nullable=False)  # DAY, SWING
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    target_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, default="")
    sector: Mapped[str] = mapped_column(default="")

    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(default="OPEN", index=True)
    # OPEN, TARGET_HIT, STOP_HIT, EXPIRED, CLOSED_MANUAL
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    report: Mapped[Report] = relationship(back_populates="recommendations")  # noqa: F821
