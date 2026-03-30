"""Use case: orchestrate the Korean news briefing pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from daily_scheduler import tz
from daily_scheduler.domain.entities.report import Report
from daily_scheduler.domain.ports.email_sender import EmailSenderPort
from daily_scheduler.domain.ports.news_provider import NewsProviderPort
from daily_scheduler.domain.ports.report_repository import (
    ReportRepositoryPort,
)
from daily_scheduler.infrastructure.adapters.claude.parser import (
    extract_html_report,
)

logger = logging.getLogger(__name__)


class RunNewsPipeline:
    """Orchestrate the Korean news briefing pipeline."""

    def __init__(
        self,
        report_repo: ReportRepositoryPort,
        news: NewsProviderPort,
        email: EmailSenderPort,
    ) -> None:
        self._report_repo = report_repo
        self._news = news
        self._email = email

    def execute(self) -> bool:
        """Run the news briefing pipeline. Returns True on success."""
        today = tz.today()

        # Idempotency check
        existing = self._report_repo.get_by_date(today, "news")
        if existing:
            logger.info(
                "News briefing for %s already exists (id=%d). Skipping.",
                today,
                existing.id,
            )
            return True

        try:
            return self._run(today)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("News briefing pipeline failed")
            self._email.send_error(
                "News briefing pipeline encountered an unexpected error. Check logs."
            )
            return False

    def _run(self, today):  # type: ignore[no-untyped-def]
        """Execute the news briefing pipeline steps."""
        # 1. Generate briefing via Claude
        logger.info("Step 1/3: Generate Korean news briefing")
        raw_response, gen_time = self._news.generate_news_briefing(today)

        if not raw_response:
            logger.error("Claude returned empty response. Sending error notification.")
            self._email.send_error("Claude CLI returned empty response for news briefing.")
            return False

        # 2. Save report
        logger.info("Step 2/3: Save report")
        html_content = extract_html_report(raw_response)
        report = Report(
            report_date=today,
            report_type="news",
            html_content=html_content,
            raw_response=raw_response,
            generation_time_s=gen_time,
        )
        self._report_repo.save(report)
        self._save_html(today, html_content)

        # 3. Send email
        logger.info("Step 3/3: Send email")
        email_sent = self._email.send(
            f"[{today}] Korean News Briefing",
            html_content,
        )
        if not email_sent:
            logger.warning("Email sending failed, but report was saved successfully")

        logger.info("News briefing pipeline completed successfully!")
        return True

    @staticmethod
    def _save_html(today, html_content: str) -> None:
        from daily_scheduler.config import get_settings

        settings = get_settings()
        db_url = settings.database_url
        reports_dir = Path(db_url.replace("sqlite:///", "")).parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        path = reports_dir / f"{today}_news.html"
        path.write_text(html_content, encoding="utf-8")
        logger.info("News briefing saved to %s", path)
