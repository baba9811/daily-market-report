"""Central configuration using pydantic-settings. Reads from .env at project root."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]  # daily-scheduler/
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: SecretStr = SecretStr("")
    email_from: str = ""
    email_to: list[str] = []

    # Claude
    claude_cli_path: str = "claude"
    claude_model: str = "sonnet"

    # Finance (optional)
    news_api_key: SecretStr = SecretStr("")
    alphavantage_key: SecretStr = SecretStr("")

    # Database
    database_url: str = f"sqlite:///{PROJECT_ROOT}/data/daily_scheduler.db"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    @field_validator("email_to", mode="before")
    @classmethod
    def parse_email_to(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            return [v] if v else []
        return v

    @property
    def db_path(self) -> Path:
        url = self.database_url.replace("sqlite:///", "")
        return Path(url)


def get_settings() -> Settings:
    return Settings()
