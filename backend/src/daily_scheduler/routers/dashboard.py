"""Dashboard router — aggregated today's data."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from daily_scheduler.database import get_db
from daily_scheduler.models.recommendation import Recommendation
from daily_scheduler.models.report import Report

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db)):
    today = date.today()

    # Latest report
    latest_report = (
        db.query(Report)
        .filter(Report.report_type == "daily")
        .order_by(Report.created_at.desc())
        .first()
    )

    # Active recommendations
    open_recs = db.query(Recommendation).filter(Recommendation.status == "OPEN").all()

    # Recent closed (last 7 days)
    week_ago = datetime.combine(today - timedelta(days=7), datetime.min.time())
    recent_closed = (
        db.query(Recommendation)
        .filter(
            Recommendation.status.in_(["TARGET_HIT", "STOP_HIT"]),
            Recommendation.closed_at >= week_ago,
        )
        .all()
    )

    # Stats
    total_closed = len(recent_closed)
    wins = sum(1 for r in recent_closed if r.status == "TARGET_HIT")
    win_rate = (wins / total_closed * 100) if total_closed > 0 else 0

    # Alerts: recommendations that just hit target/stop today
    today_alerts = [
        r for r in recent_closed
        if r.closed_at and r.closed_at.date() == today
    ]

    return {
        "latest_report": {
            "id": latest_report.id,
            "date": latest_report.report_date.isoformat(),
            "summary": latest_report.summary,
        } if latest_report else None,
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
