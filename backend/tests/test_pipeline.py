"""Tests for RunDailyPipeline use case."""

from __future__ import annotations

import json
from datetime import date
from unittest.mock import MagicMock, patch

from daily_scheduler.application.use_cases.run_daily_pipeline import (
    RunDailyPipeline,
)
from daily_scheduler.domain.entities.report import Report


def _make_finance_mock() -> MagicMock:
    """Create a finance mock that returns None for all fetch_price calls."""
    mock = MagicMock()
    mock.fetch_price.return_value = None
    return mock


def _make_pipeline(
    report_repo: MagicMock | None = None,
    rec_repo: MagicMock | None = None,
    price_repo: MagicMock | None = None,
    finance: MagicMock | None = None,
    news: MagicMock | None = None,
    email: MagicMock | None = None,
    renderer: MagicMock | None = None,
) -> RunDailyPipeline:
    return RunDailyPipeline(
        report_repo=report_repo or MagicMock(),
        rec_repo=rec_repo or MagicMock(),
        price_repo=price_repo or MagicMock(),
        finance=finance or _make_finance_mock(),
        news=news or MagicMock(),
        email=email or MagicMock(),
        renderer=renderer or MagicMock(),
    )


SAMPLE_JSON_RESPONSE = (
    "```json\n"
    + json.dumps(
        {
            "report_date": "2026-03-17",
            "market_summary": "Test summary",
            "alert_banner": "",
            "news_items": [],
            "causal_chains": [],
            "risk_matrix": [],
            "sector_analysis": [],
            "sentiment": [],
            "technicals": [],
            "recommendations": [
                {
                    "ticker": "AAPL",
                    "name": "Apple",
                    "market": "NASDAQ",
                    "direction": "LONG",
                    "timeframe": "SWING",
                    "entry_price": 185,
                    "target_price": 195,
                    "stop_loss": 180,
                    "sector": "Tech",
                    "rationale": "Strong earnings",
                    "causal_chain_summary": "Earnings → price up",
                    "risk_reward_ratio": 2.0,
                    "confidence": "high",
                }
            ],
            "upcoming_events": [],
            "past_performance_commentary": "",
            "disclaimer": "Not advice.",
        }
    )
    + "\n```"
)

# Legacy HTML format for fallback testing
SAMPLE_HTML_RESPONSE = """<!DOCTYPE html><html><body><h1>Report</h1></body></html>
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
    def test_full_pipeline_with_json_response(self, mock_save_html: MagicMock):
        report_repo = MagicMock()
        rec_repo = MagicMock()
        price_repo = MagicMock()
        finance = _make_finance_mock()
        news = MagicMock()
        email = MagicMock()
        renderer = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.return_value = []
        rec_repo.get_by_period.return_value = []
        news.generate_daily_report.return_value = (SAMPLE_JSON_RESPONSE, 5.0)
        renderer.render_daily_report.return_value = "<html>rendered</html>"
        report_repo.save.return_value = Report(
            id=42,
            report_date=date(2026, 3, 17),
            report_type="daily",
            html_content="<html>rendered</html>",
        )
        email.send.return_value = True

        pipeline = _make_pipeline(
            report_repo=report_repo,
            rec_repo=rec_repo,
            price_repo=price_repo,
            finance=finance,
            news=news,
            email=email,
            renderer=renderer,
        )
        result = pipeline.execute()

        assert result is True
        renderer.render_daily_report.assert_called_once()
        report_repo.save.assert_called_once()
        rec_repo.save_many.assert_called_once()
        email.send.assert_called_once()
        saved_recs = rec_repo.save_many.call_args[0][0]
        assert len(saved_recs) == 1
        assert saved_recs[0].ticker == "AAPL"

    @patch("daily_scheduler.application.use_cases.run_daily_pipeline.RunDailyPipeline._save_html")
    def test_falls_back_to_legacy_html(self, mock_save_html: MagicMock):
        """When JSON parse fails, pipeline falls back to legacy HTML extraction."""
        report_repo = MagicMock()
        rec_repo = MagicMock()
        news = MagicMock()
        email = MagicMock()
        renderer = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.return_value = []
        rec_repo.get_by_period.return_value = []
        news.generate_daily_report.return_value = (SAMPLE_HTML_RESPONSE, 3.0)
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
            renderer=renderer,
        )
        result = pipeline.execute()

        assert result is True
        renderer.render_daily_report.assert_not_called()
        report_repo.save.assert_called_once()
        rec_repo.save_many.assert_called_once()


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
        renderer = MagicMock()

        report_repo.get_by_date.return_value = None
        rec_repo.get_open.return_value = []
        rec_repo.get_by_period.return_value = []
        news.generate_daily_report.return_value = (SAMPLE_JSON_RESPONSE, 5.0)
        renderer.render_daily_report.return_value = "<html>rendered</html>"
        report_repo.save.return_value = Report(id=42, report_date=date(2026, 3, 17))
        email.send.return_value = False

        pipeline = _make_pipeline(
            report_repo=report_repo,
            rec_repo=rec_repo,
            news=news,
            email=email,
            renderer=renderer,
        )
        result = pipeline.execute()

        assert result is True
