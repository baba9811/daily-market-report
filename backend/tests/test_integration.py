"""Integration tests that hit real external services.

Run with: uv run pytest tests/test_integration.py -v --integration
These tests are skipped by default unless --integration flag is passed.
"""

from __future__ import annotations

import subprocess

import pytest

from daily_scheduler.config import get_settings
from daily_scheduler.infrastructure.adapters.email.smtp_sender import (
    SmtpEmailSender,
)
from daily_scheduler.infrastructure.adapters.finance.yfinance_provider import (
    YFinanceProvider,
)


def _settings_configured() -> bool:
    """Check if .env has real credentials configured."""
    s = get_settings()
    return bool(s.smtp_user and s.smtp_password.get_secret_value())


class TestSmtpIntegration:
    @pytest.mark.integration
    def test_send_test_email(self):
        """Send a real test email via SMTP."""
        settings = get_settings()
        if not settings.smtp_user:
            pytest.skip("SMTP not configured")

        sender = SmtpEmailSender(settings)
        result = sender.send(
            "[Test] Daily Scheduler - Integration Test",
            "<html><body><h1>Integration Test</h1>"
            "<p>This is an automated test email from daily-scheduler.</p>"
            "</body></html>",
        )
        assert result is True

    @pytest.mark.integration
    def test_send_error_email(self):
        """Send a real error notification email."""
        settings = get_settings()
        if not settings.smtp_user:
            pytest.skip("SMTP not configured")

        sender = SmtpEmailSender(settings)
        result = sender.send_error("Integration test error message")
        assert result is True


class TestYFinanceIntegration:
    @pytest.mark.integration
    def test_fetch_us_stock_price(self):
        """Fetch a real US stock price."""
        provider = YFinanceProvider()
        data = provider.fetch_price("AAPL")

        assert data is not None
        assert "price" in data
        assert data["price"] > 0
        assert "volume" in data

    @pytest.mark.integration
    def test_fetch_kr_stock_price(self):
        """Fetch a real Korean stock price."""
        provider = YFinanceProvider()
        data = provider.fetch_price("005930.KS")  # Samsung

        assert data is not None
        assert data["price"] > 0

    @pytest.mark.integration
    def test_fetch_invalid_ticker_returns_none(self):
        """Invalid ticker should return None, not crash."""
        provider = YFinanceProvider()
        data = provider.fetch_price("XXXXXXXXX_INVALID")
        assert data is None


class TestClaudeCLIIntegration:
    @pytest.mark.integration
    def test_claude_cli_available(self):
        """Verify Claude CLI is installed and reachable."""
        settings = get_settings()
        result = subprocess.run(
            [settings.claude_cli_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        assert result.returncode == 0

    @pytest.mark.integration
    def test_claude_cli_simple_prompt(self):
        """Run a simple Claude CLI prompt."""
        settings = get_settings()
        result = subprocess.run(
            [settings.claude_cli_path, "-p", "Reply with only: OK"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        assert result.returncode == 0
        assert result.stdout.strip()


class TestDatabaseIntegration:
    @pytest.mark.integration
    def test_database_file_exists(self):
        """Verify the database file exists at configured path."""
        settings = get_settings()
        assert settings.db_path.exists(), f"DB not found at {settings.db_path}"

    @pytest.mark.integration
    def test_database_connectable(self):
        """Verify we can connect and query the database."""
        import sqlalchemy

        from daily_scheduler.database import get_engine

        settings = get_settings()
        engine = get_engine(f"sqlite:///{settings.db_path}")
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1"))
            assert result.scalar() == 1


class TestFullPipelineIntegration:
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_daily_pipeline(self):
        """Run the full daily pipeline end-to-end.

        WARNING: This will generate a real report, call Claude CLI,
        and send a real email. Only run when you want to verify
        the entire system works.
        """
        from sqlalchemy.orm import Session

        from daily_scheduler.database import get_session_factory
        from daily_scheduler.infrastructure.dependencies import (
            get_daily_pipeline,
        )

        factory = get_session_factory()
        session: Session = factory()
        try:
            pipeline = get_daily_pipeline(session)
            result = pipeline.execute()
            session.commit()
            assert result is True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
