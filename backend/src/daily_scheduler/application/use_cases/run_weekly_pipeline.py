"""Use case: orchestrate the weekly retrospective pipeline."""

from __future__ import annotations

import logging
from datetime import date

from daily_scheduler.application.use_cases.build_retrospective import (
    BuildRetrospective,
)
from daily_scheduler.domain.entities.report import Report
from daily_scheduler.domain.ports.email_sender import EmailSenderPort
from daily_scheduler.domain.ports.news_provider import NewsProviderPort
from daily_scheduler.domain.ports.recommendation_repository import (
    RecommendationRepositoryPort,
)
from daily_scheduler.domain.ports.report_repository import (
    ReportRepositoryPort,
)
from daily_scheduler.infrastructure.adapters.claude.parser import (
    extract_html_report,
)

logger = logging.getLogger(__name__)


class RunWeeklyPipeline:
    """Orchestrate the weekly retrospective generation pipeline."""

    def __init__(
        self,
        report_repo: ReportRepositoryPort,
        rec_repo: RecommendationRepositoryPort,
        news: NewsProviderPort,
        email: EmailSenderPort,
    ) -> None:
        self._report_repo = report_repo
        self._rec_repo = rec_repo
        self._news = news
        self._email = email

    def execute(
        self, today: date | None = None,
    ) -> bool:
        """Run the weekly pipeline. Returns True on success."""
        today = today or date.today()

        try:
            retro = BuildRetrospective(self._rec_repo)
            analysis = retro.build_weekly_analysis(today)
            if not analysis:
                logger.info(
                    "No data for weekly analysis. Skipping."
                )
                return True

            # Generate report
            weekly_stats = (
                f"Wins: {analysis.win_count},"
                f" Losses: {analysis.loss_count},"
                f" Avg return:"
                f" {analysis.avg_return_pct:.1f}%"
            )
            raw_response, _ = (
                self._news.generate_weekly_report(
                    today,
                    weekly_stats,
                    analysis.sector_breakdown,
                )
            )
            if not raw_response:
                logger.error(
                    "Claude returned empty response"
                    " for weekly report"
                )
                return False

            # Save weekly report
            html_content = extract_html_report(raw_response)
            report = Report(
                report_date=today,
                report_type="weekly",
                html_content=html_content,
                raw_response=raw_response,
            )
            self._report_repo.save(report)

            # Send email
            self._email.send(
                f"[{today}] Weekly Trading"
                " Retrospective Report",
                html_content,
            )

            logger.info("Weekly pipeline completed!")
            return True

        except Exception:
            logger.exception("Weekly pipeline failed")
            return False
