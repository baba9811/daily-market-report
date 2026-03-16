"""Port: news/report generation provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date


class NewsProviderPort(ABC):
    """Abstract interface for generating reports (e.g. via Claude)."""

    @abstractmethod
    def generate_daily_report(
        self,
        report_date: date,
        retrospective_context: str,
        weekly_lessons: str = "",
    ) -> tuple[str, float]:
        """Generate a daily report.

        Returns (raw_response, generation_time_seconds).
        """

    @abstractmethod
    def generate_weekly_report(
        self,
        report_date: date,
        weekly_stats: str,
        detailed_performance: str,
    ) -> tuple[str, float]:
        """Generate a weekly retrospective report.

        Returns (raw_response, generation_time_seconds).
        """
