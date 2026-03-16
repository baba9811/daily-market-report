"""Dashboard router — aggregated today's data."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from daily_scheduler import tz
from daily_scheduler.database import get_db
from daily_scheduler.infrastructure.dependencies import (
    get_rec_repo,
    get_report_repo,
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
)


@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Return aggregated dashboard data."""
    today = tz.today()
    report_repo = get_report_repo(db)
    rec_repo = get_rec_repo(db)

    # Latest report
    latest = report_repo.get_latest("daily")

    # Active recommendations
    open_recs = rec_repo.get_open()

    # Recent closed (last 7 days)
    week_ago = tz.combine(today - timedelta(days=7))
    recent_closed = rec_repo.get_closed_by_period(week_ago)

    total_closed = len(recent_closed)
    wins = sum(1 for r in recent_closed if r.status == "TARGET_HIT")
    win_rate = wins / total_closed * 100 if total_closed > 0 else 0

    today_alerts = [r for r in recent_closed if r.closed_at and r.closed_at.date() == today]

    return {
        "latest_report": {
            "id": latest.id,
            "date": latest.report_date.isoformat(),
            "summary": latest.summary,
        }
        if latest
        else None,
        "open_recommendations": len(open_recs),
        "weekly_win_rate": round(win_rate, 1),
        "weekly_closed": total_closed,
        "alerts": [
            {
                "ticker": r.ticker,
                "name": r.name,
                "status": r.status,
                "pnl_percent": r.pnl_percent,
            }
            for r in today_alerts
        ],
    }
