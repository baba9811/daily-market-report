"""Prompt assembly service — renders Jinja2 templates with context data."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "prompts"


def get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def build_daily_prompt(
    report_date: date,
    retrospective_context: str,
    weekly_lessons: str = "",
) -> str:
    """Render the daily report prompt with context data."""
    env = get_jinja_env()
    template = env.get_template("daily_report.j2")
    return template.render(
        date=report_date.isoformat(),
        retrospective=retrospective_context,
        weekly_lessons=weekly_lessons,
    )


def build_weekly_prompt(
    report_date: date,
    weekly_stats: str,
    detailed_performance: str,
) -> str:
    """Render the weekly retrospective prompt."""
    env = get_jinja_env()
    template = env.get_template("weekly_retro.j2")
    return template.render(
        date=report_date.isoformat(),
        weekly_stats=weekly_stats,
        detailed_performance=detailed_performance,
    )
