"""Port: report persistence interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from daily_scheduler.domain.entities.report import Report


class ReportRepositoryPort(ABC):
    """Abstract interface for report persistence."""

    @abstractmethod
    def get_by_id(self, report_id: int) -> Report | None:
        ...

    @abstractmethod
    def get_latest(
        self, report_type: str = "daily",
    ) -> Report | None:
        ...

    @abstractmethod
    def get_by_date(
        self, report_date: date, report_type: str = "daily",
    ) -> Report | None:
        ...

    @abstractmethod
    def list_reports(
        self,
        report_type: str = "all",
        page: int = 1,
        per_page: int = 20,
    ) -> list[Report]:
        ...

    @abstractmethod
    def save(self, report: Report) -> Report:
        ...
