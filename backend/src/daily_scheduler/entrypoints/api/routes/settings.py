"""Settings router — view and update configuration."""

from __future__ import annotations

import subprocess

from fastapi import APIRouter

from daily_scheduler.config import ENV_FILE, get_settings
from daily_scheduler.entrypoints.api.schemas.settings import (
    SettingsOut,
    SettingsUpdate,
    StatusOut,
    TestEmailResult,
    UpdateResult,
)
from daily_scheduler.infrastructure.dependencies import (
    get_email_sender,
)

router = APIRouter(
    prefix="/api/settings",
    tags=["settings"],
)

SAFE_UPDATE_FIELDS: dict[str, str] = {
    "smtp_host": "SMTP_HOST",
    "smtp_port": "SMTP_PORT",
    "smtp_user": "SMTP_USER",
    "smtp_password": "SMTP_PASSWORD",
    "email_from": "EMAIL_FROM",
    "email_to": "EMAIL_TO",
    "claude_model": "CLAUDE_MODEL",
    "report_language": "REPORT_LANGUAGE",
}


@router.get("", response_model=SettingsOut)
def get_current_settings() -> SettingsOut:
    """Return current application settings."""
    s = get_settings()
    return SettingsOut(
        smtp_host=s.smtp_host,
        smtp_port=s.smtp_port,
        smtp_user=s.smtp_user,
        smtp_password_set=bool(
            s.smtp_password.get_secret_value(),
        ),
        email_from=s.email_from,
        email_to=s.email_to,
        claude_model=s.claude_model,
        report_language=s.report_language,
    )


@router.put("", response_model=UpdateResult)
def update_settings(update: SettingsUpdate) -> UpdateResult:
    """Update settings by writing to .env file.

    Only safe fields can be updated. Sensitive paths like
    claude_cli_path and database_url are not writable via API.
    """
    from dotenv import set_key

    env_path = str(ENV_FILE)
    updated_fields = []

    for field_name, env_key in SAFE_UPDATE_FIELDS.items():
        value = getattr(update, field_name)
        if value is not None:
            str_value = str(value) if not isinstance(value, list) else str(value)
            set_key(env_path, env_key, str_value)
            updated_fields.append(env_key)

    return UpdateResult(
        updated=updated_fields,
        message="Settings updated. Restart server to apply.",
    )


@router.post("/test-email", response_model=TestEmailResult)
def test_email() -> TestEmailResult:
    """Send a test email to verify SMTP config."""
    sender = get_email_sender()
    success = sender.send(
        "[Test] Daily Scheduler Email Test",
        "<h1>Email Test</h1><p>If you see this, your email configuration is working correctly!</p>",
    )
    return TestEmailResult(success=success)


@router.get("/status", response_model=StatusOut)
def health_check() -> StatusOut:
    """Check system health: DB, Claude CLI, SMTP."""
    settings = get_settings()

    db_ok = settings.db_path.exists()

    try:
        result = subprocess.run(
            [settings.claude_cli_path, "--version"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        cli_ok = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        cli_ok = False

    smtp_ok = bool(settings.smtp_user and settings.smtp_password.get_secret_value())

    return StatusOut(
        database=db_ok,
        claude_cli=cli_ok,
        smtp_configured=smtp_ok,
        all_ok=db_ok and cli_ok and smtp_ok,
    )
