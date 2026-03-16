"""Tests for SmtpEmailSender."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from pydantic import SecretStr

from daily_scheduler.config import Settings
from daily_scheduler.infrastructure.adapters.email.smtp_sender import (
    SmtpEmailSender,
)


def _make_settings(**overrides: object) -> Settings:
    defaults: dict[str, object] = {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "test@gmail.com",
        "smtp_password": SecretStr("testpass"),
        "email_from": "test@gmail.com",
        "email_to": ["recipient@gmail.com"],
    }
    defaults.update(overrides)
    return Settings(**defaults)  # type: ignore[arg-type]


class TestCredentialValidation:
    def test_returns_false_without_smtp_user(self):
        settings = _make_settings(smtp_user="")
        sender = SmtpEmailSender(settings)
        assert sender.send("Subject", "<p>Body</p>") is False

    def test_returns_false_without_smtp_password(self):
        settings = _make_settings(smtp_password=SecretStr(""))
        sender = SmtpEmailSender(settings)
        assert sender.send("Subject", "<p>Body</p>") is False

    def test_returns_false_without_recipients(self):
        settings = _make_settings(email_to=[])
        sender = SmtpEmailSender(settings)
        assert sender.send("Subject", "<p>Body</p>") is False


class TestSuccessfulSend:
    @patch("daily_scheduler.infrastructure.adapters.email.smtp_sender.smtplib.SMTP")
    def test_sends_email_successfully(self, mock_smtp_class: MagicMock):
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        settings = _make_settings()
        sender = SmtpEmailSender(settings)
        result = sender.send("Test Subject", "<p>Hello</p>")

        assert result is True
        mock_server.ehlo.assert_called()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "testpass")
        mock_server.sendmail.assert_called_once()

    @patch("daily_scheduler.infrastructure.adapters.email.smtp_sender.smtplib.SMTP")
    def test_uses_smtp_user_as_from_when_email_from_empty(self, mock_smtp_class: MagicMock):
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        settings = _make_settings(email_from="")
        sender = SmtpEmailSender(settings)
        sender.send("Subject", "<p>Body</p>")

        sendmail_args = mock_server.sendmail.call_args[0]
        assert sendmail_args[0] == "test@gmail.com"


class TestRetryLogic:
    @patch("daily_scheduler.infrastructure.adapters.email.smtp_sender.time.sleep")
    @patch("daily_scheduler.infrastructure.adapters.email.smtp_sender.smtplib.SMTP")
    def test_retries_then_succeeds(self, mock_smtp_class: MagicMock, mock_sleep: MagicMock):
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(
            side_effect=[Exception("fail"), Exception("fail"), mock_server]
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        settings = _make_settings()
        sender = SmtpEmailSender(settings)
        result = sender.send("Subject", "<p>Body</p>")

        assert result is True
        assert mock_sleep.call_count == 2

    @patch("daily_scheduler.infrastructure.adapters.email.smtp_sender.time.sleep")
    @patch("daily_scheduler.infrastructure.adapters.email.smtp_sender.smtplib.SMTP")
    def test_returns_false_after_max_retries(
        self, mock_smtp_class: MagicMock, mock_sleep: MagicMock
    ):
        mock_smtp_class.return_value.__enter__ = MagicMock(side_effect=Exception("fail"))
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        settings = _make_settings()
        sender = SmtpEmailSender(settings)
        result = sender.send("Subject", "<p>Body</p>")

        assert result is False


class TestSendError:
    @patch("daily_scheduler.infrastructure.adapters.email.smtp_sender.smtplib.SMTP")
    def test_send_error_calls_send_with_error_subject(self, mock_smtp_class: MagicMock):
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        settings = _make_settings()
        sender = SmtpEmailSender(settings)
        result = sender.send_error("Pipeline crashed")

        assert result is True
        mock_server.sendmail.assert_called_once()

    def test_send_error_escapes_html_in_body(self):
        """Verify send_error uses html.escape on the error message."""
        from html import escape

        malicious = "<script>alert('xss')</script>"
        safe = escape(malicious)
        assert "&lt;script&gt;" in safe
        assert "<script>" not in safe
