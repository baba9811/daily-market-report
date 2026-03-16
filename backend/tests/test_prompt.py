"""Tests for prompt assembly."""

from datetime import date
from unittest.mock import patch

from daily_scheduler.services.prompt import build_daily_prompt, build_weekly_prompt


class TestBuildDailyPrompt:
    @patch("daily_scheduler.services.prompt.get_settings")
    def test_renders_with_korean_language(self, mock_settings):
        mock_settings.return_value.report_language = "ko"
        prompt = build_daily_prompt(
            date(2026, 3, 17),
            "No past data",
            "",
        )
        assert "2026-03-17" in prompt
        assert "Korean" in prompt
        assert "No past data" in prompt

    @patch("daily_scheduler.services.prompt.get_settings")
    def test_renders_with_english_language(self, mock_settings):
        mock_settings.return_value.report_language = "en"
        prompt = build_daily_prompt(
            date(2026, 3, 17),
            "Some retrospective",
            "",
        )
        assert "English" in prompt
        assert "Some retrospective" in prompt

    @patch("daily_scheduler.services.prompt.get_settings")
    def test_includes_weekly_lessons(self, mock_settings):
        mock_settings.return_value.report_language = "ko"
        prompt = build_daily_prompt(
            date(2026, 3, 17),
            "retro context",
            "Focus on tech sector",
        )
        assert "Focus on tech sector" in prompt


class TestBuildWeeklyPrompt:
    @patch("daily_scheduler.services.prompt.get_settings")
    def test_renders_weekly_prompt(self, mock_settings):
        mock_settings.return_value.report_language = "en"
        prompt = build_weekly_prompt(
            date(2026, 3, 17),
            "Wins: 5, Losses: 3",
            '{"Technology": {"wins": 3}}',
        )
        assert "2026-03-17" in prompt
        assert "Wins: 5" in prompt
        assert "English" in prompt
