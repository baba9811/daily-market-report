"""Recommendation schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RecommendationOut(BaseModel):
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

    model_config = {"from_attributes": True}
