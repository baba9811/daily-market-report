"""Dashboard API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class LatestReportInfo(BaseModel):
    """Summary info for the latest report."""

    id: int
    date: str
    summary: str


class DashboardAlert(BaseModel):
    """An alert for a recently closed recommendation."""

    ticker: str
    name: str
    status: str
    pnl_percent: float | None


class DashboardOut(BaseModel):
    """Aggregated dashboard data."""

    latest_report: LatestReportInfo | None
    open_recommendations: int
    weekly_win_rate: float
    weekly_closed: int
    alerts: list[DashboardAlert]
