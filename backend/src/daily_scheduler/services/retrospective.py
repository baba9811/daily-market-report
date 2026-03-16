"""Retrospective service — build performance context for self-improvement."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from daily_scheduler.models.recommendation import Recommendation
from daily_scheduler.models.retrospective import Retrospective, WeeklyAnalysis

logger = logging.getLogger(__name__)


def build_daily_context(db: Session, today: date | None = None) -> str:
    """Build retrospective context text to inject into the daily prompt.

    Returns a formatted string with performance statistics and recent history.
    """
    today = today or date.today()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # 30-day aggregate stats
    all_recs = (
        db.query(Recommendation)
        .filter(Recommendation.created_at >= datetime.combine(thirty_days_ago, datetime.min.time()))
        .all()
    )

    if not all_recs:
        return "아직 과거 추천 데이터가 없습니다. 첫 번째 리포트를 생성합니다."

    total = len(all_recs)
    target_hit = sum(1 for r in all_recs if r.status == "TARGET_HIT")
    stop_hit = sum(1 for r in all_recs if r.status == "STOP_HIT")
    expired = sum(1 for r in all_recs if r.status == "EXPIRED")
    still_open = sum(1 for r in all_recs if r.status == "OPEN")

    closed_recs = [r for r in all_recs if r.pnl_percent is not None]
    avg_pnl = sum(r.pnl_percent for r in closed_recs) / len(closed_recs) if closed_recs else 0.0

    win_rate = (target_hit / (target_hit + stop_hit) * 100) if (target_hit + stop_hit) > 0 else 0.0

    best = max(closed_recs, key=lambda r: r.pnl_percent, default=None)
    worst = min(closed_recs, key=lambda r: r.pnl_percent, default=None)

    # Sector breakdown
    sector_stats: dict[str, dict[str, float]] = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0, "count": 0})
    for r in closed_recs:
        sector = r.sector or "기타"
        sector_stats[sector]["count"] += 1
        sector_stats[sector]["total_pnl"] += r.pnl_percent or 0
        if r.status == "TARGET_HIT":
            sector_stats[sector]["wins"] += 1
        elif r.status == "STOP_HIT":
            sector_stats[sector]["losses"] += 1

    # Timeframe breakdown
    day_recs = [r for r in closed_recs if r.timeframe == "DAY"]
    swing_recs = [r for r in closed_recs if r.timeframe == "SWING"]
    day_win_rate = (
        sum(1 for r in day_recs if r.status == "TARGET_HIT") / len(day_recs) * 100
        if day_recs
        else 0
    )
    swing_win_rate = (
        sum(1 for r in swing_recs if r.status == "TARGET_HIT") / len(swing_recs) * 100
        if swing_recs
        else 0
    )

    # Recent 7 days detail
    recent_recs = [
        r
        for r in all_recs
        if r.created_at >= datetime.combine(seven_days_ago, datetime.min.time())
    ]

    # Build context text
    lines = [
        "## 과거 추천 실적 (최근 30일)",
        "",
        "### 요약 통계",
        f"- 총 추천 수: {total}",
        f"- 목표가 도달: {target_hit} ({target_hit/total*100:.1f}%)",
        f"- 손절 도달: {stop_hit} ({stop_hit/total*100:.1f}%)",
        f"- 만료: {expired} ({expired/total*100:.1f}%)",
        f"- 진행 중: {still_open}",
        f"- 전체 승률: {win_rate:.1f}%",
        f"- 평균 수익률: {avg_pnl:+.1f}%",
    ]

    if best:
        lines.append(f"- 최고 수익: {best.name} ({best.ticker}) {best.pnl_percent:+.1f}%")
    if worst:
        lines.append(f"- 최대 손실: {worst.name} ({worst.ticker}) {worst.pnl_percent:+.1f}%")

    # Sector breakdown
    lines.extend(["", "### 섹터별 성과"])
    for sector, stats in sorted(sector_stats.items()):
        count = stats["count"]
        wins = stats["wins"]
        avg = stats["total_pnl"] / count if count else 0
        sr = wins / count * 100 if count else 0
        indicator = "✅ 강점" if sr >= 50 else "❌ 약점"
        lines.append(f"- {sector}: 승률 {sr:.0f}%, 평균 {avg:+.1f}% {indicator}")

    # Timeframe breakdown
    lines.extend([
        "",
        "### 전략별 성과",
        f"- 데이트레이딩: 승률 {day_win_rate:.0f}% ({len(day_recs)}건)",
        f"- 스윙트레이딩: 승률 {swing_win_rate:.0f}% ({len(swing_recs)}건)",
    ])

    # Recent detail table
    lines.extend(["", "### 최근 7일 추천 상세", "| 날짜 | 종목 | 방향 | 진입가 | 목표가 | 현재가 | 손익 | 상태 |", "|------|------|------|--------|--------|--------|------|------|"])
    for r in sorted(recent_recs, key=lambda x: x.created_at, reverse=True)[:15]:
        pnl_str = f"{r.pnl_percent:+.1f}%" if r.pnl_percent is not None else "-"
        current_str = f"{r.current_price:,.0f}" if r.current_price else "-"
        status_map = {"OPEN": "진행중", "TARGET_HIT": "✅목표도달", "STOP_HIT": "❌손절", "EXPIRED": "만료"}
        lines.append(
            f"| {r.created_at.strftime('%m-%d')} | {r.name} | {'매수' if r.direction == 'LONG' else '매도'} | "
            f"{r.entry_price:,.0f} | {r.target_price:,.0f} | {current_str} | {pnl_str} | {status_map.get(r.status, r.status)} |"
        )

    # Auto-derived lessons
    lines.extend(["", "### 교훈 (자동 도출)"])
    for sector, stats in sector_stats.items():
        count = stats["count"]
        if count >= 3:
            sr = stats["wins"] / count * 100
            if sr < 30:
                lines.append(f"- ⚠️ {sector} 섹터 추천 성공률이 {sr:.0f}%로 매우 낮음. 추천을 줄이거나 보수적 접근 필요")
            elif sr >= 70:
                lines.append(f"- 💡 {sector} 섹터 추천 성공률이 {sr:.0f}%로 우수. 이 섹터 전략 강화 권장")

    if day_recs and swing_recs:
        if swing_win_rate > day_win_rate + 10:
            lines.append(f"- 💡 스윙트레이딩({swing_win_rate:.0f}%)이 데이트레이딩({day_win_rate:.0f}%)보다 성과 우수")
        elif day_win_rate > swing_win_rate + 10:
            lines.append(f"- 💡 데이트레이딩({day_win_rate:.0f}%)이 스윙트레이딩({swing_win_rate:.0f}%)보다 성과 우수")

    context = "\n".join(lines)

    # Save to DB
    retro = Retrospective(
        report_date=today,
        recommendations_checked=len([r for r in all_recs if r.status == "OPEN"]),
        targets_hit=target_hit,
        stops_hit=stop_hit,
        expired_count=expired,
        context_block=context,
    )
    db.merge(retro)
    db.commit()

    return context


def build_weekly_analysis(db: Session, today: date | None = None) -> WeeklyAnalysis | None:
    """Build comprehensive weekly analysis for Monday reports."""
    today = today or date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    prev_week_start = week_start - timedelta(days=7)

    recs = (
        db.query(Recommendation)
        .filter(
            Recommendation.created_at >= datetime.combine(prev_week_start, datetime.min.time()),
            Recommendation.created_at < datetime.combine(week_start, datetime.min.time()),
        )
        .all()
    )

    if not recs:
        return None

    closed = [r for r in recs if r.status in ("TARGET_HIT", "STOP_HIT")]
    wins = [r for r in closed if r.status == "TARGET_HIT"]
    losses = [r for r in closed if r.status == "STOP_HIT"]
    avg_return = (
        sum(r.pnl_percent for r in closed if r.pnl_percent) / len(closed)
        if closed
        else 0.0
    )

    best = max(closed, key=lambda r: r.pnl_percent or 0, default=None)
    worst = min(closed, key=lambda r: r.pnl_percent or 0, default=None)

    # Sector breakdown
    sector_data: dict[str, dict[str, float]] = defaultdict(lambda: {"wins": 0, "losses": 0, "avg_return": 0, "count": 0})
    for r in closed:
        s = r.sector or "기타"
        sector_data[s]["count"] += 1
        sector_data[s]["avg_return"] += r.pnl_percent or 0
        if r.status == "TARGET_HIT":
            sector_data[s]["wins"] += 1
        else:
            sector_data[s]["losses"] += 1

    for s in sector_data:
        if sector_data[s]["count"] > 0:
            sector_data[s]["avg_return"] /= sector_data[s]["count"]

    analysis = WeeklyAnalysis(
        week_start=prev_week_start,
        week_end=prev_week_start + timedelta(days=6),
        total_recommendations=len(recs),
        win_count=len(wins),
        loss_count=len(losses),
        avg_return_pct=avg_return,
        best_pick_ticker=best.ticker if best else "",
        worst_pick_ticker=worst.ticker if worst else "",
        sector_breakdown=json.dumps(sector_data, ensure_ascii=False),
    )
    db.add(analysis)
    db.commit()

    return analysis
