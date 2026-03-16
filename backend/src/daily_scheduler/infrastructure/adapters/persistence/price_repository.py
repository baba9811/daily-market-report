"""SQLAlchemy implementation of PriceRepositoryPort."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from daily_scheduler.domain.entities.price import PriceSnapshot
from daily_scheduler.domain.ports.price_repository import (
    PriceRepositoryPort,
)
from daily_scheduler.infrastructure.adapters.persistence.models import (
    PriceSnapshotModel,
)


class SQLAlchemyPriceRepository(PriceRepositoryPort):
    """Persist price snapshots via SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_ticker_and_date(
        self, ticker: str, snapshot_date: date,
    ) -> PriceSnapshot | None:
        model = (
            self._db.query(PriceSnapshotModel)
            .filter(
                PriceSnapshotModel.ticker == ticker,
                PriceSnapshotModel.snapshot_date
                == snapshot_date,
            )
            .first()
        )
        return model.to_entity() if model else None

    def save(
        self, snapshot: PriceSnapshot,
    ) -> PriceSnapshot:
        model = PriceSnapshotModel.from_entity(snapshot)
        self._db.add(model)
        self._db.commit()
        return model.to_entity()
