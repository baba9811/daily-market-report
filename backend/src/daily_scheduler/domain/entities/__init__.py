"""Domain entities — pure Python dataclasses with no framework deps."""

from __future__ import annotations

from daily_scheduler.domain.entities.price import PriceSnapshot
from daily_scheduler.domain.entities.recommendation import Recommendation
from daily_scheduler.domain.entities.report import Report
from daily_scheduler.domain.entities.retrospective import (
    Retrospective,
    WeeklyAnalysis,
)

__all__ = [
    "PriceSnapshot",
    "Recommendation",
    "Report",
    "Retrospective",
    "WeeklyAnalysis",
]
