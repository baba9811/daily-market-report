"""Shared test fixtures."""

from __future__ import annotations

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


@pytest.fixture
def db() -> Session:
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    yield session
    session.close()
