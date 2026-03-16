"""Timezone-aware datetime utilities.

All datetime operations in the project MUST use these helpers
instead of datetime.now(), date.today(), or datetime.combine().
The timezone is controlled by the TIMEZONE env var (default: Asia/Seoul).
"""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from daily_scheduler.config import get_settings


def _tz() -> ZoneInfo:
    """Return the configured ZoneInfo."""
    return ZoneInfo(get_settings().timezone)


def now() -> datetime:
    """Return the current timezone-aware datetime."""
    return datetime.now(tz=_tz())


def today() -> date:
    """Return today's date in the configured timezone."""
    return now().date()


def combine(d: date, t: time | None = None) -> datetime:
    """Combine a date and time into a timezone-aware datetime.

    If time is None, uses midnight (00:00:00).
    """
    t = t or time.min
    return datetime.combine(d, t, tzinfo=_tz())
