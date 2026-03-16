"""Settings schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SettingsOut(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password_set: bool
    email_from: str
    email_to: list[str]
    claude_cli_path: str
    claude_model: str
    report_language: str
    database_url: str
    host: str
    port: int


class SettingsUpdate(BaseModel):
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None
    email_to: list[str] | None = None
    claude_cli_path: str | None = None
    claude_model: str | None = None
    report_language: str | None = None
