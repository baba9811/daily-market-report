"""Domain entities — pure Python dataclasses with no framework deps."""

from __future__ import annotations

from daily_scheduler.domain.entities.market_context import (
    FuturesData,
    IndexData,
    MarketContext,
    SectorETFData,
)
from daily_scheduler.domain.entities.price import PriceSnapshot
from daily_scheduler.domain.entities.recommendation import Recommendation
from daily_scheduler.domain.entities.report import Report
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
from daily_scheduler.domain.entities.retrospective import (
    Retrospective,
    WeeklyAnalysis,
)

__all__ = [
    "CausalChain",
    "CausalChainLink",
    "FuturesData",
    "IndexData",
    "MarketContext",
    "NewsItem",
    "PriceSnapshot",
    "RecommendationItem",
    "Recommendation",
    "Report",
    "ReportContent",
    "Retrospective",
    "RiskItem",
    "SectorETFData",
    "SectorFlow",
    "SentimentIndicator",
    "TechnicalSnapshot",
    "UpcomingEvent",
    "WeeklyAnalysis",
]
