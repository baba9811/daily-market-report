"""SMTP implementation of EmailSenderPort."""

from __future__ import annotations

import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from daily_scheduler.config import Settings
from daily_scheduler.domain.ports.email_sender import (
    EmailSenderPort,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 5


class SmtpEmailSender(EmailSenderPort):
    """Send HTML emails via SMTP with retry logic."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(
        self,
        subject: str,
        html_content: str,
    ) -> bool:
        """Send an HTML email. Returns True on success."""
        s = self._settings

        if not s.smtp_user or not s.smtp_password.get_secret_value():
            logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
            return False

        if not s.email_to:
            logger.error("No recipients configured. Set EMAIL_TO in .env")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = s.email_from or s.smtp_user
        msg["To"] = ", ".join(s.email_to)
        msg.attach(
            MIMEText(html_content, "html", "utf-8"),
        )

        for attempt in range(MAX_RETRIES):
            try:
                with smtplib.SMTP(
                    s.smtp_host,
                    s.smtp_port,
                    timeout=30,
                ) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(
                        s.smtp_user,
                        s.smtp_password.get_secret_value(),
                    )
                    server.sendmail(
                        s.email_from or s.smtp_user,
                        s.email_to,
                        msg.as_string(),
                    )
                logger.info(
                    "Email sent successfully to %s",
                    s.email_to,
                )
                return True
            except Exception:
                wait = BACKOFF_BASE * (2**attempt)
                logger.exception(
                    "Email send failed (attempt %d/%d). Retrying in %ds...",
                    attempt + 1,
                    MAX_RETRIES,
                    wait,
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(wait)

        logger.error(
            "Failed to send email after %d attempts",
            MAX_RETRIES,
        )
        return False

    def send_error(self, error_message: str) -> bool:
        """Send an error notification email."""
        html = (
            "<html><body>"
            "<h2>Daily Scheduler Error</h2>"
            "<p>The daily report pipeline encountered"
            " an error:</p>"
            f"<pre>{error_message}</pre>"
            "<p>Please check the logs for details.</p>"
            "</body></html>"
        )
        return self.send(
            "[Error] Daily Scheduler Pipeline Failed",
            html,
        )
