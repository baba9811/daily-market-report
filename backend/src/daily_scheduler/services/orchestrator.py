"""Orchestrator service — coordinates the full daily/weekly pipeline."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from daily_scheduler.config import get_settings
from daily_scheduler.models.recommendation import Recommendation
from daily_scheduler.models.report import Report
from daily_scheduler.services.claude import get_generation_time
from daily_scheduler.services.email_sender import send_email, send_error_notification
from daily_scheduler.services.finance import update_open_recommendations
from daily_scheduler.services.parser import (
    extract_html_report,
    extract_recommendations,
    extract_summary,
)
from daily_scheduler.services.prompt import build_daily_prompt, build_weekly_prompt
from daily_scheduler.services.retrospective import (
    build_daily_context,
    build_weekly_analysis,
)

logger = logging.getLogger(__name__)


def run_daily_pipeline(db: Session) -> bool:
    """Execute the full daily report pipeline.

    Returns True on success, False on failure.
    """
    today = date.today()
    settings = get_settings()

    # Idempotency: check if report already exists for today
    existing = db.query(Report).filter(
        Report.report_date == today,
        Report.report_type == "daily",
    ).first()
    if existing:
        logger.info("Daily report for %s already exists (id=%d). Skipping.", today, existing.id)
        return True

    try:
        # Step 1: Update prices for open recommendations
        logger.info("Step 1: Updating open recommendation prices...")
        updated = update_open_recommendations(db)
        logger.info("Updated %d recommendations", updated)

        # Step 2: Build retrospective context
        logger.info("Step 2: Building retrospective context...")
        retro_context = build_daily_context(db, today)

        # Step 3: Get weekly lessons if available
        weekly_lessons = ""
        if today.weekday() == 0:  # Monday
            analysis = build_weekly_analysis(db, today)
            if analysis:
                weekly_lessons = analysis.analysis_text
                logger.info("Weekly analysis built for week of %s", analysis.week_start)

        # Step 4: Assemble prompt
        logger.info("Step 3: Assembling prompt...")
        prompt = build_daily_prompt(today, retro_context, weekly_lessons)

        # Step 5: Call Claude
        logger.info("Step 4: Calling Claude Code CLI...")
        raw_response, generation_time = get_generation_time(prompt)

        if not raw_response:
            logger.error("Claude returned empty response. Sending error notification.")
            send_error_notification("Claude Code CLI returned empty response for daily report.")
            return False

        # Step 6: Parse response
        logger.info("Step 5: Parsing report...")
        html_content = extract_html_report(raw_response)
        summary = extract_summary(raw_response)
        rec_data = extract_recommendations(raw_response)

        # Step 7: Save report to DB
        report = Report(
            report_date=today,
            report_type="daily",
            html_content=html_content,
            summary=summary,
            prompt_used=prompt,
            raw_response=raw_response,
            generation_time_s=generation_time,
        )
        db.add(report)
        db.flush()  # Get the report.id

        # Step 8: Save recommendations
        for rec in rec_data:
            recommendation = Recommendation(
                report_id=report.id,
                ticker=rec.get("ticker", ""),
                name=rec.get("name", ""),
                market=rec.get("market", ""),
                direction=rec.get("direction", "LONG"),
                timeframe=rec.get("timeframe", "SWING"),
                entry_price=float(rec.get("entry_price", 0)),
                target_price=float(rec.get("target_price", 0)),
                stop_loss=float(rec.get("stop_loss", 0)),
                rationale=rec.get("rationale", ""),
                sector=rec.get("sector", ""),
            )
            db.add(recommendation)

        db.commit()
        logger.info("Saved report (id=%d) with %d recommendations", report.id, len(rec_data))

        # Step 9: Save HTML file to disk
        reports_dir = Path(settings.database_url.replace("sqlite:///", "")).parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / f"{today}_daily.html"
        report_path.write_text(html_content, encoding="utf-8")
        logger.info("Report saved to %s", report_path)

        # Step 10: Send email
        logger.info("Step 6: Sending email...")
        email_sent = send_email(
            f"[{today}] Daily News & Trading Report",
            html_content,
        )
        if not email_sent:
            logger.warning("Email sending failed, but report was saved successfully")

        # Step 11: Weekly report on Monday
        if today.weekday() == 0:
            logger.info("Monday: Running weekly retrospective...")
            run_weekly_pipeline(db, today)

        logger.info("Daily pipeline completed successfully!")
        return True

    except Exception:
        logger.exception("Daily pipeline failed")
        send_error_notification("Daily pipeline encountered an unexpected error. Check logs.")
        return False


def run_weekly_pipeline(db: Session, today: date | None = None) -> bool:
    """Execute the weekly retrospective pipeline."""
    today = today or date.today()

    try:
        analysis = build_weekly_analysis(db, today)
        if not analysis:
            logger.info("No data for weekly analysis. Skipping.")
            return True

        # Build weekly prompt
        prompt = build_weekly_prompt(
            today,
            weekly_stats=(
                f"Wins: {analysis.win_count},"
                f" Losses: {analysis.loss_count},"
                f" Avg return: {analysis.avg_return_pct:.1f}%"
            ),
            detailed_performance=analysis.sector_breakdown,
        )

        # Call Claude
        raw_response, _ = get_generation_time(prompt)
        if not raw_response:
            logger.error("Claude returned empty response for weekly report")
            return False

        # Update analysis with Claude's narrative
        analysis.analysis_text = raw_response
        db.commit()

        # Save weekly report
        html_content = extract_html_report(raw_response)
        report = Report(
            report_date=today,
            report_type="weekly",
            html_content=html_content,
            raw_response=raw_response,
        )
        db.add(report)
        db.commit()

        # Send weekly email
        send_email(
            f"[{today}] Weekly Trading Retrospective Report",
            html_content,
        )

        logger.info("Weekly pipeline completed!")
        return True

    except Exception:
        logger.exception("Weekly pipeline failed")
        return False
