"""Report DTOs for API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class ReportSummaryDTO:
    """Lightweight report summary for list views."""

    id: int
    report_date: date
    report_type: str
    summary: str
    generation_time_s: float | None
    created_at: datetime


@dataclass
class ReportDetailDTO(ReportSummaryDTO):
    """Full report detail including HTML content."""

    html_content: str = ""
