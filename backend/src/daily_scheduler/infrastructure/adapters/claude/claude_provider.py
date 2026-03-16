"""Claude CLI implementation of NewsProviderPort."""

from __future__ import annotations

import logging
import subprocess
import time
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from daily_scheduler.config import Settings
from daily_scheduler.domain.ports.news_provider import (
    NewsProviderPort,
)

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 600
TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "templates"
    / "prompts"
)


class ClaudeNewsProvider(NewsProviderPort):
    """Generate reports by calling Claude Code CLI."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._jinja = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_daily_report(
        self,
        report_date: date,
        retrospective_context: str,
        weekly_lessons: str = "",
    ) -> tuple[str, float]:
        """Generate a daily report via Claude CLI."""
        prompt = self._build_daily_prompt(
            report_date,
            retrospective_context,
            weekly_lessons,
        )
        return self._call_claude(prompt)

    def generate_weekly_report(
        self,
        report_date: date,
        weekly_stats: str,
        detailed_performance: str,
    ) -> tuple[str, float]:
        """Generate a weekly retrospective via Claude CLI."""
        prompt = self._build_weekly_prompt(
            report_date, weekly_stats,
            detailed_performance,
        )
        return self._call_claude(prompt)

    def _build_daily_prompt(
        self,
        report_date: date,
        retrospective_context: str,
        weekly_lessons: str,
    ) -> str:
        template = self._jinja.get_template(
            "daily_report.j2",
        )
        return template.render(
            date=report_date.isoformat(),
            retrospective=retrospective_context,
            weekly_lessons=weekly_lessons,
            language=self._settings.report_language,
        )

    def _build_weekly_prompt(
        self,
        report_date: date,
        weekly_stats: str,
        detailed_performance: str,
    ) -> str:
        template = self._jinja.get_template(
            "weekly_retro.j2",
        )
        return template.render(
            date=report_date.isoformat(),
            weekly_stats=weekly_stats,
            detailed_performance=detailed_performance,
            language=self._settings.report_language,
        )

    def _call_claude(
        self, prompt: str, retry: bool = True,
    ) -> tuple[str, float]:
        """Call Claude CLI and return (response, elapsed)."""
        s = self._settings
        cmd = [
            s.claude_cli_path,
            "-p",
            prompt,
            "--allowedTools",
            "WebSearch,WebFetch",
        ]
        cwd = str(s.db_path.parent.parent)

        start = time.time()
        for attempt in range(2 if retry else 1):
            try:
                logger.info(
                    "Calling Claude CLI (attempt %d)...",
                    attempt + 1,
                )
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT_SECONDS,
                    cwd=cwd,
                )
                elapsed = time.time() - start
                logger.info(
                    "Claude responded in %.1fs"
                    " (exit code: %d)",
                    elapsed,
                    result.returncode,
                )

                if result.returncode != 0:
                    logger.error(
                        "Claude CLI error (stderr): %s",
                        result.stderr[:500],
                    )
                    if attempt == 0 and retry:
                        logger.info(
                            "Retrying in 30s...",
                        )
                        time.sleep(30)
                        continue
                    return "", elapsed

                output = result.stdout.strip()
                if not output:
                    logger.warning(
                        "Claude returned empty output",
                    )
                    if attempt == 0 and retry:
                        logger.info(
                            "Retrying in 30s...",
                        )
                        time.sleep(30)
                        continue
                    return "", elapsed

                return output, elapsed

            except subprocess.TimeoutExpired:
                elapsed = time.time() - start
                logger.error(
                    "Claude CLI timed out after %ds",
                    TIMEOUT_SECONDS,
                )
                if attempt == 0 and retry:
                    time.sleep(30)
                    continue
                return "", elapsed
            except FileNotFoundError:
                elapsed = time.time() - start
                logger.error(
                    "Claude CLI not found at: %s",
                    s.claude_cli_path,
                )
                return "", elapsed

        elapsed = time.time() - start
        return "", elapsed
