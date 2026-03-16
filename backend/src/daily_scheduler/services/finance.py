"""Finance service — fetch stock prices via yfinance."""

from __future__ import annotations

import logging
from datetime import date, datetime

import yfinance as yf
from sqlalchemy.orm import Session

from daily_scheduler.models.price import PriceSnapshot
from daily_scheduler.models.recommendation import Recommendation

logger = logging.getLogger(__name__)


def fetch_price(ticker: str) -> dict | None:
    """Fetch latest price data for a single ticker. Returns None on failure."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if hist.empty:
            logger.warning("No data returned for %s", ticker)
            return None
        latest = hist.iloc[-1]
        return {
            "price": float(latest["Close"]),
            "open_price": float(latest["Open"]),
            "high": float(latest["High"]),
            "low": float(latest["Low"]),
            "volume": int(latest["Volume"]),
        }
    except Exception:
        logger.exception("Failed to fetch price for %s", ticker)
        return None


def update_open_recommendations(db: Session) -> int:
    """Fetch current prices for all OPEN recommendations and update DB.

    Also checks if target/stop-loss has been hit and updates status.
    Returns the number of recommendations updated.
    """
    open_recs = db.query(Recommendation).filter(Recommendation.status == "OPEN").all()
    updated = 0
    today = date.today()

    for rec in open_recs:
        # Auto-expire: DAY trades from previous days
        if rec.timeframe == "DAY" and rec.created_at.date() < today:
            rec.status = "EXPIRED"
            rec.closed_at = datetime.now()
            logger.info("Expired DAY recommendation: %s", rec.ticker)
            continue

        # Auto-expire: SWING trades older than 10 business days (~14 calendar days)
        days_open = (today - rec.created_at.date()).days
        if rec.timeframe == "SWING" and days_open > 14:
            rec.status = "EXPIRED"
            rec.closed_at = datetime.now()
            logger.info("Expired SWING recommendation (>14d): %s", rec.ticker)
            continue

        data = fetch_price(rec.ticker)
        if data is None:
            continue

        rec.current_price = data["price"]
        updated += 1

        # Check target/stop-loss
        if rec.direction == "LONG":
            if data["price"] >= rec.target_price:
                rec.status = "TARGET_HIT"
                rec.closed_at = datetime.now()
                rec.closed_price = data["price"]
                rec.pnl_percent = ((data["price"] - rec.entry_price) / rec.entry_price) * 100
                logger.info(
                    "TARGET HIT: %s at %.2f (%.1f%%)",
                    rec.ticker, data["price"], rec.pnl_percent,
                )
            elif data["price"] <= rec.stop_loss:
                rec.status = "STOP_HIT"
                rec.closed_at = datetime.now()
                rec.closed_price = data["price"]
                rec.pnl_percent = ((data["price"] - rec.entry_price) / rec.entry_price) * 100
                logger.info(
                    "STOP HIT: %s at %.2f (%.1f%%)",
                    rec.ticker, data["price"], rec.pnl_percent,
                )
        elif rec.direction == "SHORT":
            if data["price"] <= rec.target_price:
                rec.status = "TARGET_HIT"
                rec.closed_at = datetime.now()
                rec.closed_price = data["price"]
                rec.pnl_percent = ((rec.entry_price - data["price"]) / rec.entry_price) * 100
                logger.info(
                    "TARGET HIT (SHORT): %s at %.2f (%.1f%%)",
                    rec.ticker, data["price"], rec.pnl_percent,
                )
            elif data["price"] >= rec.stop_loss:
                rec.status = "STOP_HIT"
                rec.closed_at = datetime.now()
                rec.closed_price = data["price"]
                rec.pnl_percent = ((rec.entry_price - data["price"]) / rec.entry_price) * 100
                logger.info(
                    "STOP HIT (SHORT): %s at %.2f (%.1f%%)",
                    rec.ticker, data["price"], rec.pnl_percent,
                )

    db.commit()

    # Save price snapshots for all fetched tickers
    tickers = {rec.ticker for rec in open_recs}
    save_price_snapshots(db, tickers, today)

    return updated


def save_price_snapshots(db: Session, tickers: set[str], snapshot_date: date) -> None:
    """Save daily price snapshots for tracking history."""
    for ticker in tickers:
        existing = (
            db.query(PriceSnapshot)
            .filter(PriceSnapshot.ticker == ticker, PriceSnapshot.snapshot_date == snapshot_date)
            .first()
        )
        if existing:
            continue

        data = fetch_price(ticker)
        if data is None:
            continue

        snapshot = PriceSnapshot(
            ticker=ticker,
            snapshot_date=snapshot_date,
            price=data["price"],
            open_price=data["open_price"],
            high=data["high"],
            low=data["low"],
            volume=data["volume"],
        )
        db.add(snapshot)

    db.commit()
