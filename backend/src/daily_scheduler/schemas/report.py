"""Report schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class ReportOut(BaseModel):
    id: int
    report_date: date
    report_type: str
    summary: str
    generation_time_s: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportDetailOut(ReportOut):
    html_content: str
