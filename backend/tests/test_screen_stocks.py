"""Tests for ScreenStocks use case and ScreenedStock entity."""

from __future__ import annotations

from daily_scheduler.domain.entities.screened_stock import (
    ScreenedStock,
    ScreeningResult,
)


class TestScreenedStock:
    def test_create_minimal(self):
        stock = ScreenedStock(ticker="NVDA", name="NVIDIA", market="NASDAQ")
        assert stock.ticker == "NVDA"
        assert stock.current_price == 0.0

    def test_create_full(self):
        stock = ScreenedStock(
            ticker="005930.KS",
            name="Samsung Electronics",
            market="KOSPI",
            sector="Technology",
            current_price=185000,
            prev_close=184000,
            change_pct=0.54,
            volume=15000000,
            avg_volume=12000000,
            volume_ratio=1.25,
            week_52_high=210000,
            week_52_low=120000,
            pct_from_52w_high=-11.9,
            pct_from_52w_low=54.2,
            rsi_14=45.3,
            macd_signal="bullish_cross",
            pe_ratio=12.5,
            pb_ratio=1.2,
            roe=0.18,
        )
        assert stock.current_price == 185000
        assert stock.rsi_14 == 45.3
        assert stock.roe == 0.18


class TestScreeningResult:
    def test_empty_result(self):
        result = ScreeningResult()
        text = result.to_prompt_text()
        assert "No stock screening data" in text

    def test_to_prompt_text_includes_sections(self):
        result = ScreeningResult(
            kr_stocks=[
                ScreenedStock(
                    ticker="005930.KS",
                    name="Samsung Electronics",
                    market="KOSPI",
                    sector="Technology",
                    current_price=185000,
                    change_pct=0.5,
                    rsi_14=45.0,
                    macd_signal="neutral",
                    volume_ratio=1.2,
                    pe_ratio=12.5,
                    pb_ratio=1.2,
                    roe=0.18,
                    pct_from_52w_high=-10.0,
                    pct_from_52w_low=50.0,
                ),
            ],
            us_stocks=[
                ScreenedStock(
                    ticker="NVDA",
                    name="NVIDIA",
                    market="NASDAQ",
                    sector="Semiconductor",
                    current_price=181.0,
                    change_pct=1.2,
                    rsi_14=55.0,
                    macd_signal="bullish_cross",
                    volume_ratio=1.5,
                    pe_ratio=35.0,
                    pb_ratio=25.0,
                    roe=0.45,
                    pct_from_52w_high=-5.0,
                    pct_from_52w_low=80.0,
                ),
            ],
        )
        text = result.to_prompt_text()

        assert "Korean Stocks" in text
        assert "US Stocks" in text
        assert "005930.KS" in text
        assert "NVDA" in text
        assert "185,000" in text
        assert "RSI" in text
        assert "P/E" in text

    def test_prompt_text_with_only_us(self):
        result = ScreeningResult(
            us_stocks=[
                ScreenedStock(
                    ticker="AAPL",
                    name="Apple",
                    market="NASDAQ",
                    sector="Technology",
                    current_price=180.0,
                    change_pct=-0.5,
                    volume_ratio=0.9,
                    pct_from_52w_high=-8.0,
                    pct_from_52w_low=30.0,
                ),
            ],
        )
        text = result.to_prompt_text()
        assert "US Stocks" in text
        assert "Korean Stocks" not in text
