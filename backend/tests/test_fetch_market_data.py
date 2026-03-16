"""Tests for FetchMarketData use case."""

from __future__ import annotations

from unittest.mock import MagicMock

from daily_scheduler.application.use_cases.fetch_market_data import (
    FetchMarketData,
)

from daily_scheduler.domain.entities.market_context import (
    MarketContext,
)


class TestFetchMarketData:
    def _make_finance(self, prices: dict[str, dict | None]) -> MagicMock:
        """Create a mock finance provider that returns given prices by ticker."""
        mock = MagicMock()
        mock.fetch_price.side_effect = lambda t: prices.get(t)
        return mock

    def test_fetches_all_indices(self):
        prices = {
            "^KS11": {
                "price": 2650.0,
                "open_price": 2640.0,
                "high": 2660.0,
                "low": 2630.0,
                "volume": 100000,
            },
            "^KQ11": {
                "price": 880.0,
                "open_price": 875.0,
                "high": 885.0,
                "low": 870.0,
                "volume": 50000,
            },
            "^GSPC": {
                "price": 5200.0,
                "open_price": 5180.0,
                "high": 5210.0,
                "low": 5170.0,
                "volume": 200000,
            },
            "^IXIC": {
                "price": 16400.0,
                "open_price": 16350.0,
                "high": 16450.0,
                "low": 16300.0,
                "volume": 150000,
            },
            "^DJI": {
                "price": 39000.0,
                "open_price": 38900.0,
                "high": 39050.0,
                "low": 38850.0,
                "volume": 300000,
            },
            "USDKRW=X": {
                "price": 1340.0,
                "open_price": 1335.0,
                "high": 1345.0,
                "low": 1330.0,
                "volume": 0,
            },
            "USDJPY=X": {
                "price": 150.5,
                "open_price": 150.0,
                "high": 151.0,
                "low": 149.5,
                "volume": 0,
            },
            "EURUSD=X": {
                "price": 1.085,
                "open_price": 1.083,
                "high": 1.087,
                "low": 1.081,
                "volume": 0,
            },
            "CL=F": {
                "price": 78.5,
                "open_price": 77.8,
                "high": 79.0,
                "low": 77.5,
                "volume": 100000,
            },
            "GC=F": {
                "price": 2150.0,
                "open_price": 2140.0,
                "high": 2160.0,
                "low": 2130.0,
                "volume": 50000,
            },
            "BTC-USD": {
                "price": 68000.0,
                "open_price": 67500.0,
                "high": 68500.0,
                "low": 67000.0,
                "volume": 1000,
            },
        }
        finance = self._make_finance(prices)
        uc = FetchMarketData(finance)

        ctx = uc.execute()

        assert isinstance(ctx, MarketContext)
        assert len(ctx.indices) >= 5
        assert ctx.fx_rates["USD/KRW"] == 1340.0
        assert ctx.commodities["WTI Crude Oil"] == 78.5

    def test_skips_failed_tickers(self):
        prices = {
            "^KS11": {
                "price": 2650.0,
                "open_price": 2640.0,
                "high": 2660.0,
                "low": 2630.0,
                "volume": 100000,
            },
            "^KQ11": None,
            "^GSPC": {
                "price": 5200.0,
                "open_price": 5180.0,
                "high": 5210.0,
                "low": 5170.0,
                "volume": 200000,
            },
            "^IXIC": None,
            "^DJI": None,
            "USDKRW=X": None,
            "USDJPY=X": None,
            "EURUSD=X": None,
            "CL=F": None,
            "GC=F": None,
            "BTC-USD": None,
        }
        finance = self._make_finance(prices)
        uc = FetchMarketData(finance)

        ctx = uc.execute()

        assert len(ctx.indices) == 2
        assert len(ctx.fx_rates) == 0

    def test_change_percent_calculated_correctly(self):
        prices = {
            "^KS11": {
                "price": 2650.0,
                "open_price": 2600.0,
                "high": 2660.0,
                "low": 2590.0,
                "volume": 100000,
            },
        }
        finance = self._make_finance(prices)
        uc = FetchMarketData(finance)

        ctx = uc.execute()

        kospi = next(i for i in ctx.indices if i.ticker == "^KS11")
        # change% = (2650 - 2600) / 2600 * 100 = 1.923...
        assert abs(kospi.change_percent - 1.92) < 0.1

    def test_to_prompt_text_includes_all_sections(self):
        prices = {
            "^KS11": {
                "price": 2650.0,
                "open_price": 2640.0,
                "high": 2660.0,
                "low": 2630.0,
                "volume": 100000,
            },
            "^GSPC": {
                "price": 5200.0,
                "open_price": 5180.0,
                "high": 5210.0,
                "low": 5170.0,
                "volume": 200000,
            },
            "USDKRW=X": {
                "price": 1340.0,
                "open_price": 1335.0,
                "high": 1345.0,
                "low": 1330.0,
                "volume": 0,
            },
            "CL=F": {
                "price": 78.5,
                "open_price": 77.8,
                "high": 79.0,
                "low": 77.5,
                "volume": 100000,
            },
        }
        # Others return None
        for t in ["^KQ11", "^IXIC", "^DJI", "USDJPY=X", "EURUSD=X", "GC=F", "BTC-USD"]:
            prices[t] = None
        finance = self._make_finance(prices)
        uc = FetchMarketData(finance)

        ctx = uc.execute()
        text = ctx.to_prompt_text()

        assert "Major Indices" in text
        assert "KOSPI" in text
        assert "2,650.00" in text
        assert "FX Rates" in text
        assert "USD/KRW" in text
        assert "Commodities" in text
        assert "WTI" in text

    def test_all_failures_returns_empty_context(self):
        finance = self._make_finance({})
        uc = FetchMarketData(finance)

        ctx = uc.execute()

        assert ctx.indices == []
        assert ctx.fx_rates == {}
        assert ctx.commodities == {}
        assert "No market data" in ctx.to_prompt_text()
