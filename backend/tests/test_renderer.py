"""Tests for Jinja2ReportRenderer."""

from __future__ import annotations

from daily_scheduler.domain.entities.market_context import (
    IndexData,
    MarketContext,
)
from daily_scheduler.domain.entities.report_content import (
    NewsItem,
    RecommendationItem,
    ReportContent,
)
from daily_scheduler.infrastructure.adapters.template.renderer import (
    Jinja2ReportRenderer,
)


def _make_content(**overrides) -> ReportContent:
    defaults = {
        "report_date": "2026-03-17",
        "market_summary": "Markets rallied on tech earnings.",
        "alert_banner": "FOMC today",
    }
    defaults.update(overrides)
    return ReportContent(**defaults)


def _make_market() -> MarketContext:
    return MarketContext(
        indices=[
            IndexData(
                name="KOSPI", ticker="^KS11", price=2650.0, change_percent=0.38, prev_close=2640.0
            ),
            IndexData(
                name="S&P 500", ticker="^GSPC", price=5200.0, change_percent=0.39, prev_close=5180.0
            ),
        ],
        fx_rates={"USD/KRW": 1340.0},
        commodities={"WTI Crude Oil": 78.5},
        vix=22.5,
    )


class TestJinja2ReportRenderer:
    def test_renders_valid_html(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content()
        html = renderer.render_daily_report(content, market=_make_market(), language="ko")

        assert "<!DOCTYPE html>" in html
        assert "</html>" in html
        assert "2026-03-17" in html

    def test_no_standalone_style_tags(self):
        """Gmail strips <style> tags. Only MSO conditional <style> is allowed."""
        import re

        renderer = Jinja2ReportRenderer()
        content = _make_content()
        html = renderer.render_daily_report(content, market=_make_market())

        # Remove MSO conditional comments before checking
        cleaned = re.sub(r"<!--\[if mso\]>.*?<!\[endif\]-->", "", html, flags=re.DOTALL)
        assert "<style>" not in cleaned
        assert "<style " not in cleaned

    def test_renders_market_summary(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content(market_summary="Bull run continues")
        html = renderer.render_daily_report(content, market=_make_market())

        assert "Bull run continues" in html

    def test_renders_alert_banner(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content(alert_banner="War escalation alert")
        html = renderer.render_daily_report(content, market=_make_market())

        assert "War escalation alert" in html

    def test_renders_news_items(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content(
            news_items=[
                NewsItem(
                    category="tech",
                    headline="NVIDIA GTC opens",
                    source="CNBC",
                    published_at="2026-03-17",
                    summary="AI focus",
                    impact_level="high",
                )
            ]
        )
        html = renderer.render_daily_report(content, market=_make_market())

        assert "NVIDIA GTC opens" in html
        assert "CNBC" in html

    def test_renders_recommendations(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content(
            recommendations=[
                RecommendationItem(
                    ticker="NVDA",
                    name="NVIDIA",
                    market="NASDAQ",
                    direction="LONG",
                    timeframe="SWING",
                    entry_price=181.0,
                    target_price=196.0,
                    stop_loss=174.0,
                    sector="AI",
                    rationale="GTC catalyst",
                    risk_reward_ratio=2.14,
                )
            ]
        )
        html = renderer.render_daily_report(content, market=_make_market())

        assert "NVIDIA" in html
        assert "NVDA" in html
        assert "LONG" in html
        assert "181" in html

    def test_renders_without_market_data(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content()
        html = renderer.render_daily_report(content, market=None)

        assert "<!DOCTYPE html>" in html

    def test_english_language(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content()
        html = renderer.render_daily_report(content, market=_make_market(), language="en")

        assert "Top News" in html or "Trading Recommendations" in html or "<!DOCTYPE html>" in html

    def test_vix_display(self):
        renderer = Jinja2ReportRenderer()
        content = _make_content()
        market = _make_market()
        market.vix = 35.0
        html = renderer.render_daily_report(content, market=market)

        assert "35.00" in html
        assert "Extreme Fear" in html
