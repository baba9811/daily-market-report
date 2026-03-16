"""Email sender service — send HTML reports via Gmail SMTP."""

from __future__ import annotations

import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from daily_scheduler.config import get_settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 5  # seconds


def send_email(subject: str, html_content: str) -> bool:
    """Send an HTML email via SMTP with retry logic.

    Returns True if sent successfully, False otherwise.
    """
    settings = get_settings()

    if not settings.smtp_user or not settings.smtp_password.get_secret_value():
        logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
        return False

    if not settings.email_to:
        logger.error("No recipients configured. Set EMAIL_TO in .env")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.email_from or settings.smtp_user
    msg["To"] = ", ".join(settings.email_to)
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    for attempt in range(MAX_RETRIES):
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(settings.smtp_user, settings.smtp_password.get_secret_value())
                server.sendmail(
                    settings.email_from or settings.smtp_user,
                    settings.email_to,
                    msg.as_string(),
                )
            logger.info("Email sent successfully to %s", settings.email_to)
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

    logger.error("Failed to send email after %d attempts", MAX_RETRIES)
    return False


def send_error_notification(error_message: str) -> bool:
    """Send a simple error notification email."""
    html = f"""
    <html><body>
    <h2>Daily Scheduler Error</h2>
    <p>The daily report pipeline encountered an error:</p>
    <pre>{error_message}</pre>
    <p>Please check the logs for details.</p>
    </body></html>
    """
    return send_email("[Error] Daily Scheduler Pipeline Failed", html)
