"""Port interface for report rendering."""

from __future__ import annotations

from abc import ABC, abstractmethod

from daily_scheduler.domain.entities.market_context import MarketContext
from daily_scheduler.domain.entities.report_content import ReportContent


class ReportRendererPort(ABC):
    """Render structured report content into HTML."""

    @abstractmethod
    def render_daily_report(
        self,
        content: ReportContent,
        market: MarketContext | None = None,
        language: str = "ko",
    ) -> str:
        """Render a daily report to an HTML string."""
