"""Tests for ReportContent domain entity."""

from __future__ import annotations

from daily_scheduler.domain.entities.report_content import (
    CausalChain,
    CausalChainLink,
    NewsItem,
    RecommendationItem,
    ReportContent,
    RiskItem,
    SectorFlow,
    SentimentIndicator,
    TechnicalSnapshot,
    UpcomingEvent,
)


class TestReportContent:
    def test_minimal_creation(self):
        content = ReportContent(report_date="2026-03-17")
        assert content.report_date == "2026-03-17"
        assert content.news_items == []
        assert content.recommendations == []

    def test_full_creation(self):
        content = ReportContent(
            report_date="2026-03-17",
            market_summary="Markets rallied",
            alert_banner="FOMC today",
            news_items=[
                NewsItem(
                    category="tech",
                    headline="NVIDIA GTC",
                    source="CNBC",
                    published_at="2026-03-17",
                    summary="AI focus",
                    impact_level="high",
                    affected_sectors=["Semiconductor"],
                )
            ],
            causal_chains=[
                CausalChain(
                    title="Oil chain",
                    trigger="Iran war",
                    chain=[CausalChainLink(step="Oil up")],
                    trading_implication="Buy energy",
                )
            ],
            risk_matrix=[RiskItem(risk="War escalation", probability="medium", impact="high")],
            sector_analysis=[SectorFlow(sector="Tech", etf_ticker="XLK", change_percent=1.5)],
            sentiment=[SentimentIndicator(name="VIX", value=22.5, interpretation="fear")],
            technicals=[TechnicalSnapshot(ticker="NVDA", name="NVIDIA", rsi_14=55.0)],
            recommendations=[
                RecommendationItem(
                    ticker="NVDA",
                    name="NVIDIA",
                    market="NASDAQ",
                    direction="LONG",
                    timeframe="SWING",
                    entry_price=180.0,
                    target_price=195.0,
                    stop_loss=173.0,
                    sector="AI Semiconductor",
                    rationale="GTC catalyst",
                    risk_reward_ratio=2.14,
                )
            ],
            upcoming_events=[
                UpcomingEvent(date="2026-03-18", event="FOMC", expected_impact="high")
            ],
            past_performance_commentary="First report",
            disclaimer="Not investment advice",
        )
        assert len(content.news_items) == 1
        assert len(content.recommendations) == 1
        assert content.recommendations[0].entry_price == 180.0
        assert content.causal_chains[0].chain[0].step == "Oil up"
