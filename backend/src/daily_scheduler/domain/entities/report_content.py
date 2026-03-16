"""Structured report content — the JSON schema Claude outputs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NewsItem:
    """A single news item with source attribution."""

    category: str  # e.g. "geopolitics", "tech", "energy", "policy", "corporate"
    headline: str
    source: str
    published_at: str  # e.g. "2026-03-17 09:30 KST"
    summary: str
    impact_level: str  # "high", "medium", "low"
    affected_sectors: list[str] = field(default_factory=list)


@dataclass
class CausalChainLink:
    """One step in a causal chain: event → effect."""

    step: str


@dataclass
class CausalChain:
    """A full causal chain from trigger to trading implication."""

    title: str
    trigger: str
    chain: list[CausalChainLink] = field(default_factory=list)
    trading_implication: str = ""


@dataclass
class RiskItem:
    """A risk matrix entry."""

    risk: str
    probability: str  # "high", "medium", "low"
    impact: str  # "high", "medium", "low"
    mitigation: str = ""


@dataclass
class SectorFlow:
    """Sector ETF flow and momentum data."""

    sector: str
    etf_ticker: str
    change_percent: float = 0.0
    volume_vs_avg: float = 1.0  # 1.5 = 150% of average
    signal: str = "neutral"  # "bullish", "bearish", "neutral"


@dataclass
class TechnicalSnapshot:
    """Technical analysis snapshot for a stock or index."""

    ticker: str
    name: str
    rsi_14: float | None = None
    macd_signal: str = "neutral"  # "bullish_cross", "bearish_cross", "neutral"
    above_50d_ma: bool = True
    above_200d_ma: bool = True
    volume_ratio: float = 1.0
    week_52_high: float | None = None
    week_52_low: float | None = None
    pct_from_52w_high: float | None = None


@dataclass
class SentimentIndicator:
    """Market sentiment gauge."""

    name: str  # e.g. "VIX", "Put/Call Ratio", "Fear & Greed"
    value: float = 0.0
    interpretation: str = "neutral"
    trend: str = "stable"  # "rising", "falling", "stable"


@dataclass
class UpcomingEvent:
    """A scheduled catalyst event."""

    date: str
    event: str
    expected_impact: str = "medium"  # "high", "medium", "low"
    details: str = ""


@dataclass
class RecommendationItem:
    """A single stock recommendation."""

    ticker: str
    name: str
    market: str
    direction: str  # "LONG", "SHORT"
    timeframe: str  # "DAY", "SWING"
    entry_price: float
    target_price: float
    stop_loss: float
    sector: str = ""
    rationale: str = ""
    causal_chain_summary: str = ""
    risk_reward_ratio: float = 0.0
    confidence: str = "medium"  # "high", "medium", "low"


@dataclass
class ReportContent:
    """Full structured report — Claude outputs this as JSON, we render to HTML."""

    report_date: str
    market_summary: str = ""
    alert_banner: str = ""
    news_items: list[NewsItem] = field(default_factory=list)
    causal_chains: list[CausalChain] = field(default_factory=list)
    risk_matrix: list[RiskItem] = field(default_factory=list)
    sector_analysis: list[SectorFlow] = field(default_factory=list)
    sentiment: list[SentimentIndicator] = field(default_factory=list)
    technicals: list[TechnicalSnapshot] = field(default_factory=list)
    recommendations: list[RecommendationItem] = field(default_factory=list)
    upcoming_events: list[UpcomingEvent] = field(default_factory=list)
    past_performance_commentary: str = ""
    disclaimer: str = ""
