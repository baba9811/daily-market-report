"""Jinja2 implementation of ReportRendererPort — Gmail-compatible HTML."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from daily_scheduler.domain.entities.market_context import MarketContext
from daily_scheduler.domain.entities.report_content import ReportContent
from daily_scheduler.domain.ports.report_renderer import (
    ReportRendererPort,
)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "templates" / "email"


class Jinja2ReportRenderer(ReportRendererPort):
    """Render ReportContent to Gmail-compatible HTML via Jinja2."""

    def __init__(self) -> None:
        self._jinja = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,  # HTML is our output format
        )

    def render_daily_report(
        self,
        content: ReportContent,
        market: MarketContext | None = None,
        language: str = "ko",
    ) -> str:
        """Render daily report to HTML string."""
        template = self._jinja.get_template("daily_report.html")
        return template.render(
            report=content,
            market=market,
            language=language,
        )
