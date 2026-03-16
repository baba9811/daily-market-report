"""Port interfaces — abstract base classes defining boundaries."""

from __future__ import annotations

from daily_scheduler.domain.ports.email_sender import EmailSenderPort
from daily_scheduler.domain.ports.finance_provider import (
    FinanceProviderPort,
)
from daily_scheduler.domain.ports.news_provider import NewsProviderPort
from daily_scheduler.domain.ports.price_repository import (
    PriceRepositoryPort,
)
from daily_scheduler.domain.ports.recommendation_repository import (
    RecommendationRepositoryPort,
)
from daily_scheduler.domain.ports.report_repository import (
    ReportRepositoryPort,
)

__all__ = [
    "EmailSenderPort",
    "FinanceProviderPort",
    "NewsProviderPort",
    "PriceRepositoryPort",
    "RecommendationRepositoryPort",
    "ReportRepositoryPort",
]
