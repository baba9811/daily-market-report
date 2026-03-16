"""Performance analytics DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PerformanceSummaryDTO:
    """Aggregated performance summary."""

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


@dataclass
class SectorPerformanceDTO:
    """Per-sector performance data."""

    sector: str
    count: int
    wins: int
    losses: int
    win_rate: float
    avg_return: float


@dataclass
class TimeseriesPointDTO:
    """Single data point in a time series."""

    date: str
    win_rate: float
    cumulative_pnl: float
    recommendations_count: int
