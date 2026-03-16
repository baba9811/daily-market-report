"""Performance router — analytics and tracking data."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from daily_scheduler.database import get_db
from daily_scheduler.models.recommendation import Recommendation
from daily_scheduler.schemas.performance import (
    PerformanceSummary,
    SectorPerformance,
    TimeseriesPoint,
)
from daily_scheduler.schemas.recommendation import RecommendationOut

router = APIRouter(prefix="/api/performance", tags=["performance"])


@router.get("/summary", response_model=PerformanceSummary)
def get_summary(
    period: str = Query("30d", pattern=r"^\d+d$"),
    db: Session = Depends(get_db),
):
    days = int(period.replace("d", ""))
    since = datetime.now() - timedelta(days=days)

    recs = db.query(Recommendation).filter(Recommendation.created_at >= since).all()

    total = len(recs)
    open_count = sum(1 for r in recs if r.status == "OPEN")
    target_hit = sum(1 for r in recs if r.status == "TARGET_HIT")
    stop_hit = sum(1 for r in recs if r.status == "STOP_HIT")
    expired = sum(1 for r in recs if r.status == "EXPIRED")

    closed = [r for r in recs if r.pnl_percent is not None]
    avg_pnl = sum(r.pnl_percent for r in closed) / len(closed) if closed else 0
    win_rate = (target_hit / (target_hit + stop_hit) * 100) if (target_hit + stop_hit) > 0 else 0

    best = max(closed, key=lambda r: r.pnl_percent, default=None)
    worst = min(closed, key=lambda r: r.pnl_percent, default=None)

    return PerformanceSummary(
        total_recommendations=total,
        open_count=open_count,
        target_hit_count=target_hit,
        stop_hit_count=stop_hit,
        expired_count=expired,
        win_rate=round(win_rate, 1),
        avg_pnl=round(avg_pnl, 2),
        best_ticker=best.ticker if best else "",
        best_pnl=round(best.pnl_percent, 2) if best else 0,
        worst_ticker=worst.ticker if worst else "",
        worst_pnl=round(worst.pnl_percent, 2) if worst else 0,
    )


@router.get("/recommendations", response_model=list[RecommendationOut])
def get_recommendations(
    status: str = Query("all"),
    db: Session = Depends(get_db),
):
    query = db.query(Recommendation)
    if status != "all":
        query = query.filter(Recommendation.status == status.upper())
    return query.order_by(Recommendation.created_at.desc()).limit(100).all()


@router.get("/sectors", response_model=list[SectorPerformance])
def get_sector_performance(
    period: str = Query("30d", pattern=r"^\d+d$"),
    db: Session = Depends(get_db),
):
    days = int(period.replace("d", ""))
    since = datetime.now() - timedelta(days=days)

    closed = (
        db.query(Recommendation)
        .filter(
            Recommendation.created_at >= since,
            Recommendation.status.in_(["TARGET_HIT", "STOP_HIT"]),
        )
        .all()
    )

    sectors: dict[str, dict[str, float]] = defaultdict(
        lambda: {"count": 0, "wins": 0, "losses": 0, "total_pnl": 0}
    )
    for r in closed:
        s = r.sector or "기타"
        sectors[s]["count"] += 1
        sectors[s]["total_pnl"] += r.pnl_percent or 0
        if r.status == "TARGET_HIT":
            sectors[s]["wins"] += 1
        else:
            sectors[s]["losses"] += 1

    return [
        SectorPerformance(
            sector=sector,
            count=int(data["count"]),
            wins=int(data["wins"]),
            losses=int(data["losses"]),
            win_rate=round(data["wins"] / data["count"] * 100, 1) if data["count"] else 0,
            avg_return=round(data["total_pnl"] / data["count"], 2) if data["count"] else 0,
        )
        for sector, data in sorted(sectors.items())
    ]


@router.get("/timeseries", response_model=list[TimeseriesPoint])
def get_timeseries(
    period: str = Query("30d", pattern=r"^\d+d$"),
    db: Session = Depends(get_db),
):
    days = int(period.replace("d", ""))
    since = datetime.now() - timedelta(days=days)

    recs = (
        db.query(Recommendation)
        .filter(Recommendation.created_at >= since)
        .order_by(Recommendation.created_at)
        .all()
    )

    # Group by date
    daily: dict[str, list[Recommendation]] = defaultdict(list)
    for r in recs:
        daily[r.created_at.strftime("%Y-%m-%d")].append(r)

    points = []
    cumulative_pnl = 0.0
    for dt in sorted(daily.keys()):
        day_recs = daily[dt]
        closed = [r for r in day_recs if r.pnl_percent is not None]
        wins = sum(1 for r in closed if r.status == "TARGET_HIT")
        total_closed = len(closed)
        wr = (wins / total_closed * 100) if total_closed > 0 else 0
        cumulative_pnl += sum(r.pnl_percent for r in closed if r.pnl_percent)

        points.append(TimeseriesPoint(
            date=dt,
            win_rate=round(wr, 1),
            cumulative_pnl=round(cumulative_pnl, 2),
            recommendations_count=len(day_recs),
        ))

    return points
