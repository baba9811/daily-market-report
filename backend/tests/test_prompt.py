"""Tests for prompt assembly in claude provider."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = (
    Path(__file__).parent.parent
    / "src"
    / "daily_scheduler"
    / "templates"
    / "prompts"
)


def _render(template_name: str, **kwargs: str) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template(template_name).render(**kwargs)


class TestDailyPrompt:
    def test_renders_with_korean(self):
        prompt = _render(
            "daily_report.j2",
            date="2026-03-17",
            retrospective="No past data",
            weekly_lessons="",
            language="ko",
        )
        assert "2026-03-17" in prompt
        assert "Korean" in prompt
        assert "No past data" in prompt

    def test_renders_with_english(self):
        prompt = _render(
            "daily_report.j2",
            date="2026-03-17",
            retrospective="Some data",
            weekly_lessons="",
            language="en",
        )
        assert "English" in prompt

    def test_includes_weekly_lessons(self):
        prompt = _render(
            "daily_report.j2",
            date="2026-03-17",
            retrospective="retro",
            weekly_lessons="Focus on tech",
            language="ko",
        )
        assert "Focus on tech" in prompt


class TestWeeklyPrompt:
    def test_renders_weekly(self):
        prompt = _render(
            "weekly_retro.j2",
            date="2026-03-17",
            weekly_stats="Wins: 5, Losses: 3",
            detailed_performance='{"Tech": {"wins": 3}}',
            language="en",
        )
        assert "2026-03-17" in prompt
        assert "Wins: 5" in prompt
        assert "English" in prompt
