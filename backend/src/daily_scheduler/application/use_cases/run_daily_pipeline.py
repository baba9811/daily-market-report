"""Use case: orchestrate the full daily report pipeline."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from daily_scheduler import tz
from daily_scheduler.application.use_cases.build_retrospective import (
    BuildRetrospective,
)
from daily_scheduler.application.use_cases.check_recommendations import (
    CheckRecommendations,
)
from daily_scheduler.application.use_cases.update_prices import (
    UpdatePrices,
)
from daily_scheduler.domain.entities.recommendation import (
    Recommendation,
)
from daily_scheduler.domain.entities.report import Report
from daily_scheduler.domain.ports.email_sender import EmailSenderPort
from daily_scheduler.domain.ports.finance_provider import (
    FinanceProviderPort,
)
from daily_scheduler.domain.ports.news_provider import NewsProviderPort
from daily_scheduler.domain.ports.price_repository import (
    PriceRepositoryPort,
)
from daily_scheduler.domain.ports.recommendation_repository import (
    RecommendationRepositoryPort,
)
from daily_scheduler.domain.ports.report_repository import (
    ReportRepositoryPort,
)
from daily_scheduler.infrastructure.adapters.claude.parser import (
    extract_html_report,
    extract_recommendations,
    extract_summary,
)

logger = logging.getLogger(__name__)


class RunDailyPipeline:
    """Orchestrate the full daily report generation pipeline."""

    def __init__(
        self,
        report_repo: ReportRepositoryPort,
        rec_repo: RecommendationRepositoryPort,
        price_repo: PriceRepositoryPort,
        finance: FinanceProviderPort,
        news: NewsProviderPort,
        email: EmailSenderPort,
    ) -> None:
        self._report_repo = report_repo
        self._rec_repo = rec_repo
        self._price_repo = price_repo
        self._finance = finance
        self._news = news
        self._email = email

    def execute(self) -> bool:
        """Run the full pipeline. Returns True on success."""
        today = tz.today()

        # Idempotency check
        existing = self._report_repo.get_by_date(
            today,
            "daily",
        )
        if existing:
            logger.info(
                "Daily report for %s already exists (id=%d). Skipping.",
                today,
                existing.id,
            )
            return True

        try:
            return self._run(today)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Daily pipeline failed")
            self._email.send_error("Daily pipeline encountered an unexpected error. Check logs.")
            return False

    def _run(self, today: date) -> bool:
        # Step 1: Check recommendations (expiry, target/stop)
        logger.info("Step 1: Checking recommendations...")
        checker = CheckRecommendations(
            self._rec_repo,
            self._finance,
        )
        checker.execute()

        # Step 2: Update prices
        logger.info("Step 2: Updating prices...")
        updater = UpdatePrices(
            self._rec_repo,
            self._price_repo,
            self._finance,
        )
        updated = updater.execute()
        logger.info("Updated %d recommendations", updated)

        # Step 3: Build retrospective
        logger.info("Step 3: Building retrospective context...")
        retro_builder = BuildRetrospective(self._rec_repo)
        retro_context, _retro = retro_builder.build_daily_context(
            today,
        )

        # Step 4: Weekly lessons on Monday
        weekly_lessons = ""
        if today.weekday() == 0:
            analysis = retro_builder.build_weekly_analysis(
                today,
            )
            if analysis:
                weekly_lessons = analysis.analysis_text
                logger.info(
                    "Weekly analysis built for week of %s",
                    analysis.week_start,
                )

        # Step 5: Generate report via Claude
        logger.info("Step 4: Generating report via Claude...")
        raw_response, gen_time = self._news.generate_daily_report(
            today,
            retro_context,
            weekly_lessons,
        )

        if not raw_response:
            logger.error("Claude returned empty response. Sending error notification.")
            self._email.send_error("Claude CLI returned empty response for daily report.")
            return False

        # Step 6: Parse response
        logger.info("Step 5: Parsing report...")
        html_content = extract_html_report(raw_response)
        summary = extract_summary(raw_response)
        rec_data = extract_recommendations(raw_response)

        # Step 7: Save report
        report = Report(
            report_date=today,
            report_type="daily",
            html_content=html_content,
            summary=summary,
            prompt_used="",
            raw_response=raw_response,
            generation_time_s=gen_time,
        )
        saved_report = self._report_repo.save(report)
        if saved_report.id is None:
            raise RuntimeError("Report save did not return an ID")

        # Step 8: Save recommendations
        recs = [
            Recommendation(
                report_id=saved_report.id,
                ticker=r.get("ticker", ""),
                name=r.get("name", ""),
                market=r.get("market", ""),
                direction=r.get("direction", "LONG"),
                timeframe=r.get("timeframe", "SWING"),
                entry_price=float(
                    r.get("entry_price", 0),
                ),
                target_price=float(
                    r.get("target_price", 0),
                ),
                stop_loss=float(r.get("stop_loss", 0)),
                rationale=r.get("rationale", ""),
                sector=r.get("sector", ""),
            )
            for r in rec_data
        ]
        if recs:
            self._rec_repo.save_many(recs)

        logger.info(
            "Saved report (id=%d) with %d recommendations",
            saved_report.id,
            len(recs),
        )

        # Step 9: Save HTML to disk
        self._save_html(today, html_content)

        # Step 10: Send email
        logger.info("Step 6: Sending email...")
        email_sent = self._email.send(
            f"[{today}] Daily News & Trading Report",
            html_content,
        )
        if not email_sent:
            logger.warning("Email sending failed, but report was saved successfully")

        logger.info("Daily pipeline completed successfully!")
        return True

    @staticmethod
    def _save_html(today: date, html_content: str) -> None:
        from daily_scheduler.config import get_settings

        settings = get_settings()
        db_url = settings.database_url
        reports_dir = Path(db_url.replace("sqlite:///", "")).parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        path = reports_dir / f"{today}_daily.html"
        path.write_text(html_content, encoding="utf-8")
        logger.info("Report saved to %s", path)
