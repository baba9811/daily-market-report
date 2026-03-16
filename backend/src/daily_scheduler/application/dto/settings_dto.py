"""Settings DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingsDTO:
    """Current settings for display (no secrets)."""

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
