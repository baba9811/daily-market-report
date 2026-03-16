"""Performance router — analytics and tracking data."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from daily_scheduler import tz
from daily_scheduler.database import get_db
from daily_scheduler.domain.entities.recommendation import (
    Recommendation,
)
from daily_scheduler.entrypoints.api.schemas.performance import (
    PerformanceSummary,
    SectorPerformance,
    TimeseriesPoint,
)
from daily_scheduler.entrypoints.api.schemas.recommendation import (
    RecommendationOut,
)
from daily_scheduler.infrastructure.dependencies import (
    get_rec_repo,
)

router = APIRouter(
    prefix="/api/performance",
    tags=["performance"],
)


@router.get(
    "/summary",
    response_model=PerformanceSummary,
)
def get_summary(
    period: str = Query("30d", pattern=r"^\d+d$"),
    db: Session = Depends(get_db),
) -> PerformanceSummary:
    """Get aggregated performance summary."""
    days = int(period.replace("d", ""))
    since = tz.now() - timedelta(days=days)
    repo = get_rec_repo(db)
    recs = repo.get_by_period(since)

    total = len(recs)
    open_count = sum(1 for r in recs if r.status == "OPEN")
    target_hit = sum(1 for r in recs if r.status == "TARGET_HIT")
    stop_hit = sum(1 for r in recs if r.status == "STOP_HIT")
    expired = sum(1 for r in recs if r.status == "EXPIRED")

    closed = [r for r in recs if r.pnl_percent is not None]
    avg_pnl = sum(r.pnl_percent or 0.0 for r in closed) / len(closed) if closed else 0
    win_rate = target_hit / (target_hit + stop_hit) * 100 if (target_hit + stop_hit) > 0 else 0

    best = max(
        closed,
        key=lambda r: r.pnl_percent or 0.0,
        default=None,
    )
    worst = min(
        closed,
        key=lambda r: r.pnl_percent or 0.0,
        default=None,
    )

    return PerformanceSummary(
        total_recommendations=total,
        open_count=open_count,
        target_hit_count=target_hit,
        stop_hit_count=stop_hit,
        expired_count=expired,
        win_rate=round(win_rate, 1),
        avg_pnl=round(avg_pnl, 2),
        best_ticker=best.ticker if best else "",
        best_pnl=(round(best.pnl_percent or 0.0, 2) if best else 0),
        worst_ticker=worst.ticker if worst else "",
        worst_pnl=(round(worst.pnl_percent or 0.0, 2) if worst else 0),
    )


@router.get(
    "/recommendations",
    response_model=list[RecommendationOut],
)
def get_recommendations(
    status: str = Query("all"),
    db: Session = Depends(get_db),
) -> list[RecommendationOut]:
    """Get recommendations filtered by status."""
    repo = get_rec_repo(db)
    recs = repo.list_all(status=status)
    return [
        RecommendationOut(
            id=r.id or 0,
            report_id=r.report_id,
            ticker=r.ticker,
            name=r.name,
            market=r.market,
            direction=r.direction,
            timeframe=r.timeframe,
            entry_price=r.entry_price,
            target_price=r.target_price,
            stop_loss=r.stop_loss,
            rationale=r.rationale,
            sector=r.sector,
            current_price=r.current_price,
            status=r.status,
            pnl_percent=r.pnl_percent,
            closed_at=r.closed_at,
            created_at=r.created_at or tz.now(),
        )
        for r in recs
    ]


@router.get(
    "/sectors",
    response_model=list[SectorPerformance],
)
def get_sector_performance(
    period: str = Query("30d", pattern=r"^\d+d$"),
    db: Session = Depends(get_db),
) -> list[SectorPerformance]:
    """Get per-sector performance breakdown."""
    days = int(period.replace("d", ""))
    since = tz.now() - timedelta(days=days)
    repo = get_rec_repo(db)
    closed = repo.get_closed_by_period(since)

    sectors: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "count": 0.0,
            "wins": 0.0,
            "losses": 0.0,
            "total_pnl": 0.0,
        }
    )
    for r in closed:
        s = r.sector or "Other"
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
            win_rate=(
                round(
                    data["wins"] / data["count"] * 100,
                    1,
                )
                if data["count"]
                else 0
            ),
            avg_return=(
                round(
                    data["total_pnl"] / data["count"],
                    2,
                )
                if data["count"]
                else 0
            ),
        )
        for sector, data in sorted(sectors.items())
    ]


@router.get(
    "/timeseries",
    response_model=list[TimeseriesPoint],
)
def get_timeseries(
    period: str = Query("30d", pattern=r"^\d+d$"),
    db: Session = Depends(get_db),
) -> list[TimeseriesPoint]:
    """Get time series performance data."""
    days = int(period.replace("d", ""))
    since = tz.now() - timedelta(days=days)
    repo = get_rec_repo(db)
    recs = repo.get_by_period(since)

    daily: dict[str, list[Recommendation]] = defaultdict(
        list,
    )
    for r in recs:
        if r.created_at:
            key = r.created_at.strftime("%Y-%m-%d")
            daily[key].append(r)

    points = []
    cumulative_pnl = 0.0
    for dt in sorted(daily.keys()):
        day_recs = daily[dt]
        closed = [r for r in day_recs if r.pnl_percent is not None]
        wins = sum(1 for r in closed if r.status == "TARGET_HIT")
        total_closed = len(closed)
        wr = wins / total_closed * 100 if total_closed > 0 else 0
        cumulative_pnl += sum(r.pnl_percent for r in closed if r.pnl_percent)

        points.append(
            TimeseriesPoint(
                date=dt,
                win_rate=round(wr, 1),
                cumulative_pnl=round(
                    cumulative_pnl,
                    2,
                ),
                recommendations_count=len(day_recs),
            )
        )

    return points
