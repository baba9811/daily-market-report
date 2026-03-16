"""SQLAlchemy engine and session factory."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from daily_scheduler.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""


def get_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine."""
    url = database_url or get_settings().database_url
    return create_engine(url, echo=False, connect_args={"check_same_thread": False})


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Create a session factory bound to an engine."""
    engine = get_engine(database_url)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after use."""
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
