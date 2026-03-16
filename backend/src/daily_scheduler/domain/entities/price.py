"""PriceSnapshot entity — pure Python dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class PriceSnapshot:
    """A daily price record for a tracked ticker."""

    ticker: str
    snapshot_date: date
    price: float
    open_price: float | None = None
    high: float | None = None
    low: float | None = None
    volume: int | None = None
    id: int | None = None
    created_at: datetime | None = field(default=None)
