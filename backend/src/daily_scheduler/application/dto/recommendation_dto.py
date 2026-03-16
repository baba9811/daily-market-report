"""Recommendation DTOs for API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class RecommendationDTO:
    """Recommendation data for API responses."""

    id: int
    report_id: int
    ticker: str
    name: str
    market: str
    direction: str
    timeframe: str
    entry_price: float
    target_price: float
    stop_loss: float
    rationale: str
    sector: str
    current_price: float | None
    status: str
    pnl_percent: float | None
    closed_at: datetime | None
    created_at: datetime
