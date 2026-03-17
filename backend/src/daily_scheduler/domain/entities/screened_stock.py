"""ScreenedStock entity — pre-fetched stock data for analyst-grade recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScreenedStock:
    """A stock with pre-fetched fundamental + technical data."""

    ticker: str
    name: str
    market: str  # "KOSPI", "KOSDAQ", "NYSE", "NASDAQ"
    sector: str = ""
    industry: str = ""

    # Price data (verified from yfinance)
    current_price: float = 0.0
    prev_close: float = 0.0
    change_pct: float = 0.0
    volume: int = 0
    avg_volume: int = 0
    volume_ratio: float = 1.0  # current / avg

    # 52-week range
    week_52_high: float = 0.0
    week_52_low: float = 0.0
    pct_from_52w_high: float = 0.0
    pct_from_52w_low: float = 0.0

    # Technical indicators
    rsi_14: float | None = None
    macd_signal: str = ""  # "bullish_cross", "bearish_cross", "neutral"
    sma_50: float | None = None
    sma_200: float | None = None
    above_sma_50: bool | None = None
    above_sma_200: bool | None = None

    # Fundamentals
    market_cap: float = 0.0  # in local currency
    pe_ratio: float | None = None  # trailing P/E
    forward_pe: float | None = None
    pb_ratio: float | None = None
    peg_ratio: float | None = None
    roe: float | None = None  # as decimal (0.25 = 25%)
    debt_to_equity: float | None = None
    profit_margin: float | None = None
    revenue_growth: float | None = None
    earnings_growth: float | None = None
    dividend_yield: float | None = None
    free_cashflow: float | None = None
    beta: float | None = None


@dataclass
class ScreeningResult:
    """Collection of screened stocks for prompt inclusion."""

    kr_stocks: list[ScreenedStock] = field(default_factory=list)
    us_stocks: list[ScreenedStock] = field(default_factory=list)
    screening_errors: int = 0

    def to_prompt_text(self) -> str:
        """Format screening data as a structured table for Claude."""
        if not self.kr_stocks and not self.us_stocks:
            return "No stock screening data available."

        lines: list[str] = []

        for label, stocks in [
            ("Korean Stocks (KOSPI/KOSDAQ)", self.kr_stocks),
            ("US Stocks (NYSE/NASDAQ)", self.us_stocks),
        ]:
            if not stocks:
                continue
            lines.append(f"### {label}")
            lines.append(
                "| Ticker | Name | Price | Chg% | RSI | MACD | Vol Ratio "
                "| P/E | P/B | ROE% | 52wH% | 52wL% | Sector |"
            )
            lines.append(
                "|--------|------|------:|-----:|----:|------|----------:"
                "|----:|----:|-----:|------:|------:|--------|"
            )
            for s in stocks:
                rsi_str = f"{s.rsi_14:.0f}" if s.rsi_14 is not None else "-"
                pe_str = f"{s.pe_ratio:.1f}" if s.pe_ratio is not None else "-"
                pb_str = f"{s.pb_ratio:.1f}" if s.pb_ratio is not None else "-"
                roe_str = f"{s.roe * 100:.1f}" if s.roe is not None else "-"
                macd_str = (
                    "▲"
                    if "bullish" in s.macd_signal
                    else "▼"
                    if "bearish" in s.macd_signal
                    else "—"
                )
                lines.append(
                    f"| {s.ticker} | {s.name[:15]} | {s.current_price:,.0f} "
                    f"| {'+' if s.change_pct >= 0 else ''}{s.change_pct:.1f}% "
                    f"| {rsi_str} | {macd_str} | {s.volume_ratio:.1f}x "
                    f"| {pe_str} | {pb_str} | {roe_str} "
                    f"| {s.pct_from_52w_high:.1f}% | +{s.pct_from_52w_low:.1f}% "
                    f"| {s.sector[:12]} |"
                )
            lines.append("")

        return "\n".join(lines)
