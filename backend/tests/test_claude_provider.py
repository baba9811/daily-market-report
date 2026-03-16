"""Tests for ClaudeNewsProvider."""

from __future__ import annotations

import subprocess
from datetime import date
from unittest.mock import MagicMock, patch

from daily_scheduler.config import Settings
from daily_scheduler.infrastructure.adapters.claude.claude_provider import (
    ClaudeNewsProvider,
)


def _make_settings() -> Settings:
    return Settings(
        claude_cli_path="claude",
        claude_model="sonnet",
        report_language="ko",
    )


class TestBuildPrompts:
    def test_build_daily_prompt(self):
        provider = ClaudeNewsProvider(_make_settings())
        prompt = provider._build_daily_prompt(
            date(2026, 3, 17),
            "retro context",
            "weekly lessons",
            "KOSPI: 2650.00",
        )
        assert "2026-03-17" in prompt
        assert "retro context" in prompt
        assert "weekly lessons" in prompt
        assert "KOSPI: 2650.00" in prompt

    def test_build_weekly_prompt(self):
        provider = ClaudeNewsProvider(_make_settings())
        prompt = provider._build_weekly_prompt(
            date(2026, 3, 17),
            "Wins: 5",
            '{"Tech": {"wins": 3}}',
        )
        assert "2026-03-17" in prompt
        assert "Wins: 5" in prompt


class TestCallClaude:
    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_successful_call(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="<html>report</html>",
            stderr="",
        )

        provider = ClaudeNewsProvider(_make_settings())
        response, elapsed = provider._call_claude("test prompt", retry=False)

        assert response == "<html>report</html>"
        assert elapsed > 0

    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_returns_empty_on_nonzero_exit(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error occurred",
        )

        provider = ClaudeNewsProvider(_make_settings())
        response, _ = provider._call_claude("test", retry=False)

        assert response == ""

    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_returns_empty_on_empty_output(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )

        provider = ClaudeNewsProvider(_make_settings())
        response, _ = provider._call_claude("test", retry=False)

        assert response == ""

    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_handles_timeout(self, mock_run: MagicMock):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=600)

        provider = ClaudeNewsProvider(_make_settings())
        response, _ = provider._call_claude("test", retry=False)

        assert response == ""

    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_handles_file_not_found(self, mock_run: MagicMock):
        mock_run.side_effect = FileNotFoundError()

        provider = ClaudeNewsProvider(_make_settings())
        response, _ = provider._call_claude("test", retry=False)

        assert response == ""

    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.time.sleep")
    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_retries_on_failure(self, mock_run: MagicMock, mock_sleep: MagicMock):
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout="", stderr="fail"),
            MagicMock(returncode=0, stdout="<html>ok</html>", stderr=""),
        ]

        provider = ClaudeNewsProvider(_make_settings())
        response, _ = provider._call_claude("test", retry=True)

        assert response == "<html>ok</html>"
        assert mock_run.call_count == 2
        mock_sleep.assert_called_once_with(30)


class TestGenerateReport:
    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_generate_daily_report(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="<html>daily report</html>",
            stderr="",
        )

        provider = ClaudeNewsProvider(_make_settings())
        response, elapsed = provider.generate_daily_report(
            date(2026, 3, 17),
            "retro",
            "",
        )

        assert "daily report" in response
        mock_run.assert_called_once()

    @patch("daily_scheduler.infrastructure.adapters.claude.claude_provider.subprocess.run")
    def test_generate_weekly_report(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="<html>weekly report</html>",
            stderr="",
        )

        provider = ClaudeNewsProvider(_make_settings())
        response, elapsed = provider.generate_weekly_report(
            date(2026, 3, 17),
            "stats",
            "{}",
        )

        assert "weekly report" in response
