"""Settings API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SettingsOut(BaseModel):
    """Current settings (no secrets or sensitive paths)."""

    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password_set: bool
    email_from: str
    email_to: list[str]
    claude_model: str
    report_language: str


class SettingsUpdate(BaseModel):
    """Partial settings update.

    Only safe fields are writable. Sensitive paths like
    claude_cli_path and database_url cannot be changed via API.
    """

    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None
    email_to: list[str] | None = None
    claude_model: str | None = None
    report_language: str | None = None


class StatusOut(BaseModel):
    """System health status."""

    database: bool
    claude_cli: bool
    smtp_configured: bool
    all_ok: bool


class UpdateResult(BaseModel):
    """Result of a settings update."""

    updated: list[str]
    message: str


class TestEmailResult(BaseModel):
    """Result of a test email."""

    success: bool
