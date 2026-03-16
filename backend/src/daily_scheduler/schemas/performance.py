"""Performance analytics schemas."""

from __future__ import annotations

from pydantic import BaseModel


class PerformanceSummary(BaseModel):
    total_recommendations: int
    open_count: int
    target_hit_count: int
    stop_hit_count: int
    expired_count: int
    win_rate: float
    avg_pnl: float
    best_ticker: str
    best_pnl: float
    worst_ticker: str
    worst_pnl: float


class SectorPerformance(BaseModel):
    sector: str
    count: int
    wins: int
    losses: int
    win_rate: float
    avg_return: float


class TimeseriesPoint(BaseModel):
    date: str
    win_rate: float
    cumulative_pnl: float
    recommendations_count: int
