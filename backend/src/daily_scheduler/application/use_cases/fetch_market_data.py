"""Use case: fetch real-time market data for report generation."""

from __future__ import annotations

import logging

from daily_scheduler.domain.entities.market_context import (
    IndexData,
    MarketContext,
)
from daily_scheduler.domain.ports.finance_provider import (
    FinanceProviderPort,
)

logger = logging.getLogger(__name__)

# Ticker definitions for market data collection
INDICES = [
    ("KOSPI", "^KS11"),
    ("KOSDAQ", "^KQ11"),
    ("S&P 500", "^GSPC"),
    ("NASDAQ", "^IXIC"),
    ("Dow Jones", "^DJI"),
]

FX_TICKERS = [
    ("USD/KRW", "USDKRW=X"),
    ("USD/JPY", "USDJPY=X"),
    ("EUR/USD", "EURUSD=X"),
]

COMMODITY_TICKERS = [
    ("WTI Crude Oil", "CL=F"),
    ("Gold", "GC=F"),
    ("Bitcoin", "BTC-USD"),
]


class FetchMarketData:
    """Fetch major indices, FX rates, and commodity prices."""

    def __init__(self, finance: FinanceProviderPort) -> None:
        self._finance = finance

    def execute(self) -> MarketContext:
        """Fetch all market data and return a MarketContext."""
        ctx = MarketContext()

        # Indices
        for name, ticker in INDICES:
            data = self._finance.fetch_price(ticker)
            if data is None:
                logger.warning("Failed to fetch index: %s (%s)", name, ticker)
                continue
            price = data["price"]
            open_price = data["open_price"]
            change_pct = ((price - open_price) / open_price * 100) if open_price else 0.0
            ctx.indices.append(
                IndexData(
                    name=name,
                    ticker=ticker,
                    price=round(price, 2),
                    change_percent=round(change_pct, 2),
                    prev_close=round(open_price, 2),
                )
            )

        # FX rates
        for pair, ticker in FX_TICKERS:
            data = self._finance.fetch_price(ticker)
            if data is None:
                logger.warning("Failed to fetch FX: %s (%s)", pair, ticker)
                continue
            ctx.fx_rates[pair] = round(data["price"], 2)

        # Commodities
        for name, ticker in COMMODITY_TICKERS:
            data = self._finance.fetch_price(ticker)
            if data is None:
                logger.warning("Failed to fetch commodity: %s (%s)", name, ticker)
                continue
            ctx.commodities[name] = round(data["price"], 2)

        logger.info(
            "Fetched market data: %d indices, %d FX, %d commodities",
            len(ctx.indices),
            len(ctx.fx_rates),
            len(ctx.commodities),
        )
        return ctx
