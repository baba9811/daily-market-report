"""Claude CLI implementation of NewsProviderPort."""

from __future__ import annotations

import logging
import subprocess
import time
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from daily_scheduler.config import Settings
from daily_scheduler.constants import (
    CLAUDE_RETRY_COUNT,
    CLAUDE_RETRY_DELAY_SECONDS,
    CLAUDE_TIMEOUT_SECONDS,
)
from daily_scheduler.domain.ports.news_provider import (
    NewsProviderPort,
)

logger = logging.getLogger(__name__)
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "templates" / "prompts"


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
        market_data: str = "",
        screening_data: str = "",
    ) -> tuple[str, float]:
        """Generate a daily report via Claude CLI."""
        prompt = self._build_daily_prompt(
            report_date,
            retrospective_context,
            weekly_lessons,
            market_data,
            screening_data,
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
            report_date,
            weekly_stats,
            detailed_performance,
        )
        return self._call_claude(prompt)

    def generate_news_briefing(
        self,
        report_date: date,
    ) -> tuple[str, float]:
        """Generate a Korean domestic news/events briefing via Claude CLI."""
        prompt = self._build_news_prompt(report_date)
        return self._call_claude(prompt)

    def generate_global_news_briefing(
        self,
        report_date: date,
    ) -> tuple[str, float]:
        """Generate an international/global news briefing via Claude CLI."""
        prompt = self._build_global_news_prompt(report_date)
        return self._call_claude(prompt)

    def _build_daily_prompt(
        self,
        report_date: date,
        retrospective_context: str,
        weekly_lessons: str,
        market_data: str,
        screening_data: str,
    ) -> str:
        template = self._jinja.get_template(
            "daily_report.j2",
        )
        return template.render(
            date=report_date.isoformat(),
            retrospective=retrospective_context,
            weekly_lessons=weekly_lessons,
            market_data=market_data,
            screening_data=screening_data,
            language=self._settings.report_language,
        )

    def _build_news_prompt(
        self,
        report_date: date,
    ) -> str:
        template = self._jinja.get_template(
            "korean_news.j2",
        )
        return template.render(
            date=report_date.isoformat(),
            language=self._settings.report_language,
        )

    def _build_global_news_prompt(
        self,
        report_date: date,
    ) -> str:
        template = self._jinja.get_template(
            "global_news.j2",
        )
        return template.render(
            date=report_date.isoformat(),
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
        self,
        prompt: str,
        retry: bool = True,
    ) -> tuple[str, float]:
        """Call Claude CLI and return (response, elapsed)."""

        s = self._settings
        cmd = [
            s.claude_cli_path,
            "-p",
            prompt,
            "--model",
            s.claude_model,
            "--effort",
            "max",
            "--output-format",
            "text",
            "--permission-mode",
            "bypassPermissions",
            "--tools",
            "WebSearch,WebFetch",
            "--disallowed-tools",
            "Write,Edit,Bash,ExitPlanMode,EnterPlanMode,TodoWrite",
        ]
        cwd = str(s.db_path.parent.parent)

        start = time.time()
        attempts = CLAUDE_RETRY_COUNT if retry else 1
        for attempt in range(attempts):
            try:
                logger.info(
                    "Calling Claude CLI (attempt %d)...",
                    attempt + 1,
                )
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=CLAUDE_TIMEOUT_SECONDS,
                    cwd=cwd,
                    check=False,
                )
                elapsed = time.time() - start
                logger.info(
                    "Claude responded in %.1fs (exit code: %d)",
                    elapsed,
                    result.returncode,
                )

                if result.returncode != 0:
                    logger.error(
                        "Claude CLI error (stderr): %s",
                        result.stderr[:500],
                    )
                    if attempt < attempts - 1:
                        logger.info(
                            "Retrying in %ds...",
                            CLAUDE_RETRY_DELAY_SECONDS,
                        )
                        time.sleep(CLAUDE_RETRY_DELAY_SECONDS)
                        continue
                    return "", elapsed

                output = result.stdout.strip()
                if not output:
                    logger.warning(
                        "Claude returned empty output",
                    )
                    if attempt < attempts - 1:
                        logger.info(
                            "Retrying in %ds...",
                            CLAUDE_RETRY_DELAY_SECONDS,
                        )
                        time.sleep(CLAUDE_RETRY_DELAY_SECONDS)
                        continue
                    return "", elapsed

                return output, elapsed

            except subprocess.TimeoutExpired:
                elapsed = time.time() - start
                logger.error(
                    "Claude CLI timed out after %ds",
                    CLAUDE_TIMEOUT_SECONDS,
                )
                if attempt < attempts - 1:
                    time.sleep(CLAUDE_RETRY_DELAY_SECONDS)
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
