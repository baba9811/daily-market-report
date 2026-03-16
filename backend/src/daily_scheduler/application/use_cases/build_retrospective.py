"""Use case: build retrospective context for daily/weekly prompts."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import date, timedelta

from daily_scheduler import tz
from daily_scheduler.domain.entities.recommendation import (
    Recommendation,
)
from daily_scheduler.domain.entities.retrospective import (
    Retrospective,
    WeeklyAnalysis,
)
from daily_scheduler.domain.ports.recommendation_repository import (
    RecommendationRepositoryPort,
)

logger = logging.getLogger(__name__)


class BuildRetrospective:
    """Build performance context from past recommendations."""

    def __init__(
        self,
        rec_repo: RecommendationRepositoryPort,
    ) -> None:
        self._rec_repo = rec_repo

    def build_daily_context(
        self,
        today: date | None = None,
    ) -> tuple[str, Retrospective]:
        """Build retrospective context text for the daily prompt.

        Returns (context_text, retrospective_entity).
        """
        today = today or tz.today()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)

        since_30d = tz.combine(thirty_days_ago)
        all_recs = self._rec_repo.get_by_period(since_30d)

        if not all_recs:
            retro = Retrospective(
                report_date=today,
                context_block=("No past recommendation data available. Generating first report."),
            )
            return retro.context_block, retro

        context = self._format_context(
            all_recs,
            today,
            seven_days_ago,
        )

        open_count = sum(1 for r in all_recs if r.status == "OPEN")
        target_hit = sum(1 for r in all_recs if r.status == "TARGET_HIT")
        stop_hit = sum(1 for r in all_recs if r.status == "STOP_HIT")
        expired = sum(1 for r in all_recs if r.status == "EXPIRED")

        retro = Retrospective(
            report_date=today,
            recommendations_checked=open_count,
            targets_hit=target_hit,
            stops_hit=stop_hit,
            expired_count=expired,
            context_block=context,
        )
        return context, retro

    def build_weekly_analysis(
        self,
        today: date | None = None,
    ) -> WeeklyAnalysis | None:
        """Build weekly analysis for Monday reports."""
        today = today or tz.today()
        week_start = today - timedelta(days=today.weekday())
        prev_week_start = week_start - timedelta(days=7)

        since = tz.combine(prev_week_start)
        until = tz.combine(week_start)

        all_recs = self._rec_repo.get_by_period(since)
        recs = [r for r in all_recs if r.created_at and r.created_at < until]

        if not recs:
            return None

        closed = [r for r in recs if r.status in ("TARGET_HIT", "STOP_HIT")]
        wins = [r for r in closed if r.status == "TARGET_HIT"]
        losses = [r for r in closed if r.status == "STOP_HIT"]
        avg_return = (
            sum(r.pnl_percent for r in closed if r.pnl_percent) / len(closed) if closed else 0.0
        )

        best = max(
            closed,
            key=lambda r: r.pnl_percent or 0,
            default=None,
        )
        worst = min(
            closed,
            key=lambda r: r.pnl_percent or 0,
            default=None,
        )

        sector_data = self._build_sector_breakdown(closed)

        return WeeklyAnalysis(
            week_start=prev_week_start,
            week_end=prev_week_start + timedelta(days=6),
            total_recommendations=len(recs),
            win_count=len(wins),
            loss_count=len(losses),
            avg_return_pct=avg_return,
            best_pick_ticker=best.ticker if best else "",
            worst_pick_ticker=worst.ticker if worst else "",
            sector_breakdown=json.dumps(
                sector_data,
                ensure_ascii=False,
            ),
        )

    def _format_context(
        self,
        all_recs: list[Recommendation],
        today: date,
        seven_days_ago: date,
    ) -> str:
        """Format the retrospective context text."""
        total = len(all_recs)
        target_hit = sum(1 for r in all_recs if r.status == "TARGET_HIT")
        stop_hit = sum(1 for r in all_recs if r.status == "STOP_HIT")
        expired = sum(1 for r in all_recs if r.status == "EXPIRED")
        still_open = sum(1 for r in all_recs if r.status == "OPEN")

        closed_recs = [r for r in all_recs if r.pnl_percent is not None]
        avg_pnl = (
            sum(r.pnl_percent or 0.0 for r in closed_recs) / len(closed_recs)
            if closed_recs
            else 0.0
        )
        win_rate = (
            target_hit / (target_hit + stop_hit) * 100 if (target_hit + stop_hit) > 0 else 0.0
        )

        best = max(
            closed_recs,
            key=lambda r: r.pnl_percent,
            default=None,
        )
        worst = min(
            closed_recs,
            key=lambda r: r.pnl_percent,
            default=None,
        )

        sector_stats = self._build_sector_stats(closed_recs)

        day_recs = [r for r in closed_recs if r.timeframe == "DAY"]
        swing_recs = [r for r in closed_recs if r.timeframe == "SWING"]
        day_wr = self._win_rate(day_recs)
        swing_wr = self._win_rate(swing_recs)

        since_7d = tz.combine(seven_days_ago)
        recent_recs = [r for r in all_recs if r.created_at and r.created_at >= since_7d]

        lines = [
            "## Past Recommendation Performance (Last 30 Days)",
            "",
            "### Summary Statistics",
            f"- Total recommendations: {total}",
            f"- Target hit: {target_hit} ({target_hit / total * 100:.1f}%)",
            f"- Stop loss hit: {stop_hit} ({stop_hit / total * 100:.1f}%)",
            f"- Expired: {expired} ({expired / total * 100:.1f}%)",
            f"- Open: {still_open}",
            f"- Overall win rate: {win_rate:.1f}%",
            f"- Average return: {avg_pnl:+.1f}%",
        ]

        if best:
            lines.append(f"- Best profit: {best.name} ({best.ticker}) {best.pnl_percent:+.1f}%")
        if worst:
            lines.append(f"- Worst loss: {worst.name} ({worst.ticker}) {worst.pnl_percent:+.1f}%")

        lines.extend(["", "### Sector Performance"])
        for sector, stats in sorted(sector_stats.items()):
            count = stats["count"]
            wins = stats["wins"]
            avg = stats["total_pnl"] / count if count else 0
            sr = wins / count * 100 if count else 0
            indicator = "Strong" if sr >= 50 else "Weak"
            lines.append(f"- {sector}: Win rate {sr:.0f}%, Avg {avg:+.1f}% {indicator}")

        lines.extend(
            [
                "",
                "### Strategy Performance",
                f"- Day trading: Win rate {day_wr:.0f}% ({len(day_recs)} trades)",
                f"- Swing trading: Win rate {swing_wr:.0f}% ({len(swing_recs)} trades)",
            ]
        )

        lines.extend(
            [
                "",
                "### Recent 7-Day Recommendations",
                "| Date | Stock | Direction | Entry | Target | Current | P&L | Status |",
                "|------|-------|-----------|------|--------|---------|-----|--------|",
            ]
        )
        sorted_recent = sorted(
            recent_recs,
            key=lambda x: x.created_at or tz.combine(date.min),
            reverse=True,
        )[:15]
        for r in sorted_recent:
            pnl_str = f"{r.pnl_percent:+.1f}%" if r.pnl_percent is not None else "-"
            current_str = f"{r.current_price:,.0f}" if r.current_price else "-"
            status_map = {
                "OPEN": "Open",
                "TARGET_HIT": "Target Hit",
                "STOP_HIT": "Stop Hit",
                "EXPIRED": "Expired",
            }
            direction = "Buy" if r.direction == "LONG" else "Sell"
            date_str = r.created_at.strftime("%m-%d") if r.created_at else "?"
            status = status_map.get(r.status, r.status)
            lines.append(
                f"| {date_str} | {r.name} | {direction}"
                f" | {r.entry_price:,.0f}"
                f" | {r.target_price:,.0f}"
                f" | {current_str}"
                f" | {pnl_str} | {status} |"
            )

        lines.extend(["", "### Lessons (Auto-derived)"])
        self._add_lessons(
            lines,
            sector_stats,
            day_recs,
            swing_recs,
            day_wr,
            swing_wr,
        )

        return "\n".join(lines)

    @staticmethod
    def _win_rate(
        recs: list[Recommendation],
    ) -> float:
        if not recs:
            return 0.0
        wins = sum(1 for r in recs if r.status == "TARGET_HIT")
        return wins / len(recs) * 100

    @staticmethod
    def _build_sector_stats(
        closed_recs: list[Recommendation],
    ) -> dict[str, dict[str, float]]:
        def _default() -> dict[str, float]:
            return {
                "wins": 0,
                "losses": 0,
                "total_pnl": 0,
                "count": 0,
            }

        stats: dict[str, dict[str, float]] = defaultdict(
            _default,
        )
        for r in closed_recs:
            sector = r.sector or "Other"
            stats[sector]["count"] += 1
            stats[sector]["total_pnl"] += r.pnl_percent or 0
            if r.status == "TARGET_HIT":
                stats[sector]["wins"] += 1
            elif r.status == "STOP_HIT":
                stats[sector]["losses"] += 1
        return dict(stats)

    @staticmethod
    def _build_sector_breakdown(
        closed: list[Recommendation],
    ) -> dict[str, dict[str, float]]:
        def _default() -> dict[str, float]:
            return {
                "wins": 0,
                "losses": 0,
                "avg_return": 0,
                "count": 0,
            }

        data: dict[str, dict[str, float]] = defaultdict(
            _default,
        )
        for r in closed:
            s = r.sector or "Other"
            data[s]["count"] += 1
            data[s]["avg_return"] += r.pnl_percent or 0
            if r.status == "TARGET_HIT":
                data[s]["wins"] += 1
            else:
                data[s]["losses"] += 1

        for s in data:
            if data[s]["count"] > 0:
                data[s]["avg_return"] /= data[s]["count"]

        return dict(data)

    @staticmethod
    def _add_lessons(
        lines: list[str],
        sector_stats: dict[str, dict[str, float]],
        day_recs: list[Recommendation],
        swing_recs: list[Recommendation],
        day_wr: float,
        swing_wr: float,
    ) -> None:
        for sector, stats in sector_stats.items():
            count = stats["count"]
            if count >= 3:
                sr = stats["wins"] / count * 100
                if sr < 30:
                    lines.append(
                        f"- Warning: {sector} sector win"
                        f" rate is {sr:.0f}%, very low."
                        " Reduce exposure or use more"
                        " conservative approach."
                    )
                elif sr >= 70:
                    lines.append(
                        f"- Tip: {sector} sector win rate"
                        f" is {sr:.0f}%, excellent."
                        " Consider increasing allocation"
                        " to this sector."
                    )

        if day_recs and swing_recs:
            if swing_wr > day_wr + 10:
                lines.append(
                    f"- Tip: Swing trading ({swing_wr:.0f}%)"
                    f" outperforms day trading"
                    f" ({day_wr:.0f}%)."
                )
            elif day_wr > swing_wr + 10:
                lines.append(
                    f"- Tip: Day trading ({day_wr:.0f}%)"
                    f" outperforms swing trading"
                    f" ({swing_wr:.0f}%)."
                )
