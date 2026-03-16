"""Tests for RunDailyPipeline use case."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

from daily_scheduler.application.use_cases.run_daily_pipeline import (
    RunDailyPipeline,
)
from daily_scheduler.domain.entities.report import Report


def _make_pipeline(
    report_repo: MagicMock | None = None,
    rec_repo: MagicMock | None = None,
    price_repo: MagicMock | None = None,
    finance: MagicMock | None = None,
    news: MagicMock | None = None,
    email: MagicMock | None = None,
) -> RunDailyPipeline:
    return RunDailyPipeline(
        report_repo=report_repo or MagicMock(),
        rec_repo=rec_repo or MagicMock(),
        price_repo=price_repo or MagicMock(),
        finance=finance or MagicMock(),
        news=news or MagicMock(),
        email=email or MagicMock(),
    )


SAMPLE_RESPONSE = """<!DOCTYPE html><html><body><h1>Report</h1></body></html>
<!-- REC_START
[{"ticker": "AAPL", "name": "Apple", "market": "NASDAQ",
  "direction": "LONG", "timeframe": "SWING",
  "entry_price": 185, "target_price": 195, "stop_loss": 180,
  "sector": "Tech", "rationale": "Strong earnings"}]
REC_END -->"""


class TestIdempotency:
    def test_skips_if_report_already_exists(self):
        report_repo = MagicMock()
        report_repo.get_by_date.return_value = Report(
            id=1,
            report_date=date(2026, 3, 17),
            report_type="daily",
        )
        pipeline = _make_pipeline(report_repo=report_repo)
        result = pipeline.execute()

        assert result is True
        report_repo.save.assert_not_called()


class TestSuccessfulRun:
    @patch("daily_scheduler.application.use_cases.run_daily_pipeline.RunDailyPipeline._save_html")
    def test_full_pipeline_succeeds(self, mock_save_html: MagicMock):
        report_repo = MagicMock()
        rec_repo = MagicMock()
        price_repo = MagicMock()
        finance = MagicMock()
        news = MagicMock()
        email = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.return_value = []
        rec_repo.get_by_period.return_value = []
        news.generate_daily_report.return_value = (SAMPLE_RESPONSE, 5.0)
        report_repo.save.return_value = Report(
            id=42,
            report_date=date(2026, 3, 17),
            report_type="daily",
            html_content="<html>test</html>",
        )
        email.send.return_value = True

        pipeline = _make_pipeline(
            report_repo=report_repo,
            rec_repo=rec_repo,
            price_repo=price_repo,
            finance=finance,
            news=news,
            email=email,
        )
        result = pipeline.execute()

        assert result is True
        report_repo.save.assert_called_once()
        rec_repo.save_many.assert_called_once()
        email.send.assert_called_once()
        saved_recs = rec_repo.save_many.call_args[0][0]
        assert len(saved_recs) == 1
        assert saved_recs[0].ticker == "AAPL"


class TestEmptyClaudeResponse:
    def test_returns_false_on_empty_response(self):
        report_repo = MagicMock()
        rec_repo = MagicMock()
        news = MagicMock()
        email = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.return_value = []
        rec_repo.get_by_period.return_value = []
        news.generate_daily_report.return_value = ("", 0.0)

        pipeline = _make_pipeline(
            report_repo=report_repo,
            rec_repo=rec_repo,
            news=news,
            email=email,
        )
        result = pipeline.execute()

        assert result is False
        email.send_error.assert_called_once()


class TestExceptionHandling:
    def test_catches_exception_and_sends_error_email(self):
        report_repo = MagicMock()
        rec_repo = MagicMock()
        email = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.side_effect = RuntimeError("DB connection failed")

        pipeline = _make_pipeline(
            report_repo=report_repo,
            rec_repo=rec_repo,
            email=email,
        )
        result = pipeline.execute()

        assert result is False
        email.send_error.assert_called_once()


class TestNoRecommendationsParsed:
    @patch("daily_scheduler.application.use_cases.run_daily_pipeline.RunDailyPipeline._save_html")
    def test_saves_report_without_recs(self, mock_save_html: MagicMock):
        report_repo = MagicMock()
        rec_repo = MagicMock()
        news = MagicMock()
        email = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.return_value = []
        rec_repo.get_by_period.return_value = []
        news.generate_daily_report.return_value = (
            "<!DOCTYPE html><html><body>No recs</body></html>",
            3.0,
        )
        report_repo.save.return_value = Report(
            id=10,
            report_date=date(2026, 3, 17),
        )
        email.send.return_value = True

        pipeline = _make_pipeline(
            report_repo=report_repo,
            rec_repo=rec_repo,
            news=news,
            email=email,
        )
        result = pipeline.execute()

        assert result is True
        report_repo.save.assert_called_once()
        rec_repo.save_many.assert_not_called()


class TestEmailFailure:
    @patch("daily_scheduler.application.use_cases.run_daily_pipeline.RunDailyPipeline._save_html")
    def test_returns_true_even_if_email_fails(self, mock_save_html: MagicMock):
        report_repo = MagicMock()
        rec_repo = MagicMock()
        news = MagicMock()
        email = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.return_value = []
        rec_repo.get_by_period.return_value = []
        news.generate_daily_report.return_value = (SAMPLE_RESPONSE, 5.0)
        report_repo.save.return_value = Report(id=42, report_date=date(2026, 3, 17))
        email.send.return_value = False

        pipeline = _make_pipeline(
            report_repo=report_repo,
            rec_repo=rec_repo,
            news=news,
            email=email,
        )
        result = pipeline.execute()

        assert result is True
