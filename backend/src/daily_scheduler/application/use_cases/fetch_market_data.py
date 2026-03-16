"""Use case: fetch real-time market data for report generation."""

from __future__ import annotations

import logging

from daily_scheduler.domain.entities.market_context import (
    FuturesData,
    IndexData,
    MarketContext,
    SectorETFData,
)
from daily_scheduler.domain.ports.finance_provider import (
    FinanceProviderPort,
)

logger = logging.getLogger(__name__)

# ── Ticker definitions ──────────────────────────────────────
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

FUTURES_TICKERS = [
    ("S&P 500 Futures", "ES=F"),
    ("NASDAQ Futures", "NQ=F"),
    ("Dow Futures", "YM=F"),
]

VIX_TICKER = ("VIX", "^VIX")

SECTOR_ETF_TICKERS = [
    ("Technology", "XLK"),
    ("Financials", "XLF"),
    ("Energy", "XLE"),
    ("Healthcare", "XLV"),
    ("Consumer Disc.", "XLY"),
    ("Industrials", "XLI"),
    ("Communication", "XLC"),
    ("Materials", "XLB"),
    ("Real Estate", "XLRE"),
    ("Utilities", "XLU"),
    ("Consumer Staples", "XLP"),
]


class FetchMarketData:
    """Fetch major indices, FX rates, commodity prices, futures, VIX, and sector ETFs."""

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

        # US equity futures
        for name, ticker in FUTURES_TICKERS:
            data = self._finance.fetch_price(ticker)
            if data is None:
                logger.warning("Failed to fetch futures: %s (%s)", name, ticker)
                continue
            price = data["price"]
            open_price = data["open_price"]
            change_pct = ((price - open_price) / open_price * 100) if open_price else 0.0
            ctx.futures.append(
                FuturesData(
                    name=name,
                    ticker=ticker,
                    price=round(price, 2),
                    change_percent=round(change_pct, 2),
                )
            )

        # VIX
        vix_data = self._finance.fetch_price(VIX_TICKER[1])
        if vix_data is not None:
            ctx.vix = round(vix_data["price"], 2)
        else:
            logger.warning("Failed to fetch VIX")

        # Sector ETFs
        for name, ticker in SECTOR_ETF_TICKERS:
            data = self._finance.fetch_price(ticker)
            if data is None:
                logger.warning("Failed to fetch sector ETF: %s (%s)", name, ticker)
                continue
            price = data["price"]
            open_price = data["open_price"]
            change_pct = ((price - open_price) / open_price * 100) if open_price else 0.0
            ctx.sector_etfs.append(
                SectorETFData(
                    name=name,
                    ticker=ticker,
                    price=round(price, 2),
                    change_percent=round(change_pct, 2),
                    volume=int(data.get("volume", 0)),
                )
            )

        logger.info(
            "Fetched market data: %d indices, %d FX, %d commodities, "
            "%d futures, VIX=%s, %d sector ETFs",
            len(ctx.indices),
            len(ctx.fx_rates),
            len(ctx.commodities),
            len(ctx.futures),
            ctx.vix,
            len(ctx.sector_etfs),
        )
        return ctx
