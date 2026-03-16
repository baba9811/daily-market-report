"""Shared test fixtures."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from daily_scheduler.database import Base
from daily_scheduler.infrastructure.adapters.persistence.models import (  # noqa: F401
    PriceSnapshotModel,
    RecommendationModel,
    ReportModel,
    RetrospectiveModel,
    WeeklyAnalysisModel,
)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add --integration CLI flag."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests that hit real external services",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Skip integration tests unless --integration is passed."""
    if config.getoption("--integration"):
        return
    skip = pytest.mark.skip(reason="need --integration flag to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    yield session
    session.close()
