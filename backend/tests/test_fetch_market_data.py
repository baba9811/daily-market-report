"""Tests for FetchMarketData use case."""

from __future__ import annotations

from unittest.mock import MagicMock

from daily_scheduler.application.use_cases.fetch_market_data import (
    FetchMarketData,
)
from daily_scheduler.domain.entities.market_context import (
    MarketContext,
)


def _price(p: float, o: float, h: float, low: float, v: int = 100000) -> dict:
    return {"price": p, "open_price": o, "high": h, "low": low, "volume": v}


# All tickers that FetchMarketData will try to fetch
ALL_TICKERS = {
    # Indices
    "^KS11": _price(2650.0, 2640.0, 2660.0, 2630.0),
    "^KQ11": _price(880.0, 875.0, 885.0, 870.0, 50000),
    "^GSPC": _price(5200.0, 5180.0, 5210.0, 5170.0, 200000),
    "^IXIC": _price(16400.0, 16350.0, 16450.0, 16300.0, 150000),
    "^DJI": _price(39000.0, 38900.0, 39050.0, 38850.0, 300000),
    # FX
    "USDKRW=X": _price(1340.0, 1335.0, 1345.0, 1330.0, 0),
    "USDJPY=X": _price(150.5, 150.0, 151.0, 149.5, 0),
    "EURUSD=X": _price(1.085, 1.083, 1.087, 1.081, 0),
    # Commodities
    "CL=F": _price(78.5, 77.8, 79.0, 77.5),
    "GC=F": _price(2150.0, 2140.0, 2160.0, 2130.0, 50000),
    "BTC-USD": _price(68000.0, 67500.0, 68500.0, 67000.0, 1000),
    # Futures
    "ES=F": _price(5210.0, 5195.0, 5220.0, 5190.0),
    "NQ=F": _price(16450.0, 16380.0, 16500.0, 16350.0),
    "YM=F": _price(39100.0, 39000.0, 39150.0, 38950.0),
    # VIX
    "^VIX": _price(22.5, 21.8, 23.0, 21.5, 0),
    # Sector ETFs
    "XLK": _price(210.0, 208.5, 211.0, 208.0, 500000),
    "XLF": _price(42.0, 41.8, 42.2, 41.5, 400000),
    "XLE": _price(95.0, 94.0, 96.0, 93.5, 300000),
    "XLV": _price(145.0, 144.5, 145.5, 144.0, 200000),
    "XLY": _price(180.0, 179.0, 181.0, 178.5, 250000),
    "XLI": _price(115.0, 114.5, 115.5, 114.0, 180000),
    "XLC": _price(82.0, 81.5, 82.5, 81.0, 150000),
    "XLB": _price(88.0, 87.5, 88.5, 87.0, 120000),
    "XLRE": _price(40.0, 39.8, 40.2, 39.5, 100000),
    "XLU": _price(70.0, 69.8, 70.3, 69.5, 90000),
    "XLP": _price(78.0, 77.8, 78.3, 77.5, 110000),
}


def _make_finance(prices: dict[str, dict | None]) -> MagicMock:
    mock = MagicMock()
    mock.fetch_price.side_effect = lambda t: prices.get(t)
    return mock


class TestFetchMarketData:
    def test_fetches_all_data(self):
        finance = _make_finance(ALL_TICKERS)
        uc = FetchMarketData(finance)
        ctx = uc.execute()

        assert isinstance(ctx, MarketContext)
        assert len(ctx.indices) == 5
        assert ctx.fx_rates["USD/KRW"] == 1340.0
        assert ctx.commodities["WTI Crude Oil"] == 78.5
        assert len(ctx.futures) == 3
        assert ctx.vix == 22.5
        assert len(ctx.sector_etfs) == 11

    def test_skips_failed_tickers(self):
        prices = {
            "^KS11": _price(2650.0, 2640.0, 2660.0, 2630.0),
            "^GSPC": _price(5200.0, 5180.0, 5210.0, 5170.0),
        }
        finance = _make_finance(prices)
        uc = FetchMarketData(finance)
        ctx = uc.execute()

        assert len(ctx.indices) == 2
        assert len(ctx.fx_rates) == 0
        assert len(ctx.futures) == 0
        assert ctx.vix is None
        assert len(ctx.sector_etfs) == 0

    def test_change_percent_calculated_correctly(self):
        prices = {"^KS11": _price(2650.0, 2600.0, 2660.0, 2590.0)}
        finance = _make_finance(prices)
        uc = FetchMarketData(finance)
        ctx = uc.execute()

        kospi = next(i for i in ctx.indices if i.ticker == "^KS11")
        assert abs(kospi.change_percent - 1.92) < 0.1

    def test_futures_change_percent(self):
        prices = {"ES=F": _price(5210.0, 5195.0, 5220.0, 5190.0)}
        finance = _make_finance(prices)
        uc = FetchMarketData(finance)
        ctx = uc.execute()

        assert len(ctx.futures) == 1
        assert ctx.futures[0].name == "S&P 500 Futures"
        assert ctx.futures[0].change_percent > 0

    def test_sector_etf_volume(self):
        prices = {"XLK": _price(210.0, 208.5, 211.0, 208.0, 500000)}
        finance = _make_finance(prices)
        uc = FetchMarketData(finance)
        ctx = uc.execute()

        assert len(ctx.sector_etfs) == 1
        assert ctx.sector_etfs[0].volume == 500000

    def test_to_prompt_text_includes_all_sections(self):
        finance = _make_finance(ALL_TICKERS)
        uc = FetchMarketData(finance)
        ctx = uc.execute()
        text = ctx.to_prompt_text()

        assert "Major Indices" in text
        assert "KOSPI" in text
        assert "US Equity Futures" in text
        assert "VIX" in text
        assert "Sector ETF" in text
        assert "FX Rates" in text
        assert "Commodities" in text

    def test_all_failures_returns_empty_context(self):
        finance = _make_finance({})
        uc = FetchMarketData(finance)
        ctx = uc.execute()

        assert ctx.indices == []
        assert ctx.fx_rates == {}
        assert ctx.commodities == {}
        assert ctx.futures == []
        assert ctx.vix is None
        assert ctx.sector_etfs == []
        assert "No market data" in ctx.to_prompt_text()
