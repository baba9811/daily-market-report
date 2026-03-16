"""yfinance implementation of FinanceProviderPort."""

from __future__ import annotations

import logging

import yfinance as yf

from daily_scheduler.domain.ports.finance_provider import (
    FinanceProviderPort,
)

logger = logging.getLogger(__name__)


class YFinanceProvider(FinanceProviderPort):
    """Fetch stock prices via yfinance."""

    def fetch_price(self, ticker: str) -> dict[str, float | int] | None:
        """Fetch latest price data for a single ticker."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if hist.empty:
                logger.warning(
                    "No data returned for %s",
                    ticker,
                )
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
            logger.exception(
                "Failed to fetch price for %s",
                ticker,
            )
            return None
