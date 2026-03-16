"""Settings router — view and update configuration."""

from __future__ import annotations

from fastapi import APIRouter

from daily_scheduler.config import ENV_FILE, get_settings
from daily_scheduler.schemas.settings import SettingsOut, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsOut)
def get_current_settings():
    s = get_settings()
    return SettingsOut(
        smtp_host=s.smtp_host,
        smtp_port=s.smtp_port,
        smtp_user=s.smtp_user,
        smtp_password_set=bool(s.smtp_password.get_secret_value()),
        email_from=s.email_from,
        email_to=s.email_to,
        claude_cli_path=s.claude_cli_path,
        claude_model=s.claude_model,
        database_url=s.database_url,
        host=s.host,
        port=s.port,
    )


@router.put("")
def update_settings(update: SettingsUpdate):
    """Update settings by writing to .env file."""
    from dotenv import set_key

    env_path = str(ENV_FILE)
    updated_fields = []

    field_map = {
        "smtp_host": "SMTP_HOST",
        "smtp_port": "SMTP_PORT",
        "smtp_user": "SMTP_USER",
        "smtp_password": "SMTP_PASSWORD",
        "email_from": "EMAIL_FROM",
        "email_to": "EMAIL_TO",
        "claude_cli_path": "CLAUDE_CLI_PATH",
        "claude_model": "CLAUDE_MODEL",
    }

    for field_name, env_key in field_map.items():
        value = getattr(update, field_name)
        if value is not None:
            str_value = str(value) if not isinstance(value, list) else str(value)
            set_key(env_path, env_key, str_value)
            updated_fields.append(env_key)

    return {"updated": updated_fields, "message": "Settings updated. Restart server to apply."}


@router.post("/test-email")
def test_email():
    """Send a test email to verify SMTP configuration."""
    from daily_scheduler.services.email_sender import send_email

    success = send_email(
        "[Test] Daily Scheduler Email Test",
        "<h1>Email Test</h1><p>If you see this, your email configuration is working correctly!</p>",
    )
    return {"success": success}


@router.get("/status")
def health_check():
    """Check system health: DB, Claude CLI, SMTP."""
    import subprocess

    from daily_scheduler.config import get_settings

    settings = get_settings()
    status = {}

    # DB
    status["database"] = settings.db_path.exists()

    # Claude CLI
    try:
        result = subprocess.run(
            [settings.claude_cli_path, "--version"],
            capture_output=True,
            timeout=5,
        )
        status["claude_cli"] = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        status["claude_cli"] = False

    # SMTP config
    status["smtp_configured"] = bool(
        settings.smtp_user and settings.smtp_password.get_secret_value()
    )

    status["all_ok"] = all(status.values())
    return status
