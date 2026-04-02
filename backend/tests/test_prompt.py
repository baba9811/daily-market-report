"""Tests for prompt assembly in claude provider."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "src" / "daily_scheduler" / "templates" / "prompts"


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

    def test_includes_macro_reflection_step(self):
        prompt = _render(
            "daily_report.j2",
            date="2026-03-17",
            retrospective="retro data",
            weekly_lessons="",
            language="en",
        )
        assert "Macroeconomic Reflection" in prompt
        assert "Microeconomic Reflection" in prompt
        assert "Strategic Recalibration" in prompt
        assert "STEP 2.5" in prompt

    def test_retrospective_data_in_step_2_5(self):
        prompt = _render(
            "daily_report.j2",
            date="2026-03-17",
            retrospective="my retro context here",
            weekly_lessons="",
            language="en",
        )
        step_2_5_pos = prompt.find("STEP 2.5")
        step_3_pos = prompt.find("STEP 3")
        retro_pos = prompt.find("my retro context here")
        assert step_2_5_pos < retro_pos < step_3_pos


class TestWeeklyPrompt:
    def test_renders_weekly(self):
        prompt = _render(
            "weekly_retro.j2",
            date="2026-03-17",
            weekly_stats="Wins: 5, Losses: 3",
            detailed_performance='{"Tech": {"wins": 3}}',
            closed_trade_rationales="",
            language="en",
        )
        assert "2026-03-17" in prompt
        assert "Wins: 5" in prompt
        assert "English" in prompt

    def test_includes_macro_micro_analysis(self):
        prompt = _render(
            "weekly_retro.j2",
            date="2026-03-17",
            weekly_stats="Wins: 3, Losses: 2",
            detailed_performance="{}",
            closed_trade_rationales="",
            language="en",
        )
        assert "Macroeconomic Impact Analysis" in prompt
        assert "Microeconomic Impact Analysis" in prompt
        assert "Root Cause Analysis" in prompt

    def test_includes_closed_rationales(self):
        rationales = "- AAPL (Apple): WIN (+5.2%) | Rationale: Strong AI demand"
        prompt = _render(
            "weekly_retro.j2",
            date="2026-03-17",
            weekly_stats="Wins: 1",
            detailed_performance="{}",
            closed_trade_rationales=rationales,
            language="en",
        )
        assert "Strong AI demand" in prompt
        assert "Closed Trade Rationales" in prompt
