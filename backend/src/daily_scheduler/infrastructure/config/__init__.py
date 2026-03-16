"""Infrastructure config — re-exports from root config."""

from __future__ import annotations

from daily_scheduler.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
