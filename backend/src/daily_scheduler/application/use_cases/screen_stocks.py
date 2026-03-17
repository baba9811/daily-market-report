"""Use case: screen a universe of stocks with fundamental + technical data."""

from __future__ import annotations

import logging
import math

import yfinance as yf

from daily_scheduler.domain.entities.screened_stock import (
    ScreenedStock,
    ScreeningResult,
)

logger = logging.getLogger(__name__)

# ── Stock Universe ──────────────────────────────────────────
# Popular and mid-cap stocks across sectors. Claude will select from these
# based on news, catalysts, and data signals — NOT just blue chips.

KR_TICKERS: list[tuple[str, str, str]] = [
    # Semiconductor / IT
    ("005930.KS", "Samsung Electronics", "KOSPI"),
    ("000660.KS", "SK Hynix", "KOSPI"),
    ("042700.KS", "Hanmi Semiconductor", "KOSPI"),
    ("403870.KS", "HPSP", "KOSPI"),
    ("058470.KS", "Rino Industrial", "KOSPI"),
    # Platform / Internet
    ("035420.KS", "NAVER", "KOSPI"),
    ("035720.KS", "Kakao", "KOSPI"),
    ("263750.KS", "Pearl Abyss", "KOSPI"),
    # Battery / EV
    ("373220.KS", "LG Energy Solution", "KOSPI"),
    ("006400.KS", "Samsung SDI", "KOSPI"),
    ("247540.KS", "Ecopro BM", "KOSPI"),
    ("086520.KS", "Ecopro", "KOSPI"),
    # Defense / Shipbuilding
    ("012450.KS", "Hanwha Aerospace", "KOSPI"),
    ("042660.KS", "Hanwha Ocean", "KOSPI"),
    ("329180.KS", "HD Hyundai Heavy", "KOSPI"),
    # Auto
    ("005380.KS", "Hyundai Motor", "KOSPI"),
    ("000270.KS", "Kia", "KOSPI"),
    # Bio / Pharma
    ("207940.KS", "Samsung Biologics", "KOSPI"),
    ("068270.KS", "Celltrion", "KOSPI"),
    ("326030.KQ", "SK Biopharmaceuticals", "KOSDAQ"),
    # Energy / Chemical
    ("096770.KS", "SK Innovation", "KOSPI"),
    ("010950.KS", "S-Oil", "KOSPI"),
    ("051910.KS", "LG Chem", "KOSPI"),
    # Finance
    ("105560.KS", "KB Financial", "KOSPI"),
    ("055550.KS", "Shinhan Financial", "KOSPI"),
    # Telecom / Media
    ("017670.KS", "SK Telecom", "KOSPI"),
    ("030200.KS", "KT", "KOSPI"),
    # Consumer / Retail
    ("004170.KS", "Shinsegae", "KOSPI"),
    ("069960.KQ", "Hyundai Department Store", "KOSDAQ"),
    # Industrial / Construction
    ("000120.KS", "CJ Logistics", "KOSPI"),
]

US_TICKERS: list[tuple[str, str, str]] = [
    # Mega-cap Tech
    ("NVDA", "NVIDIA", "NASDAQ"),
    ("AAPL", "Apple", "NASDAQ"),
    ("MSFT", "Microsoft", "NASDAQ"),
    ("GOOGL", "Alphabet", "NASDAQ"),
    ("AMZN", "Amazon", "NASDAQ"),
    ("META", "Meta Platforms", "NASDAQ"),
    ("TSLA", "Tesla", "NASDAQ"),
    # Semiconductor
    ("TSM", "TSMC", "NYSE"),
    ("AMD", "AMD", "NASDAQ"),
    ("MU", "Micron Technology", "NASDAQ"),
    ("AVGO", "Broadcom", "NASDAQ"),
    ("QCOM", "Qualcomm", "NASDAQ"),
    # AI / Software
    ("PLTR", "Palantir", "NASDAQ"),
    ("CRM", "Salesforce", "NYSE"),
    ("NOW", "ServiceNow", "NYSE"),
    ("SNOW", "Snowflake", "NYSE"),
    # Energy
    ("XOM", "Exxon Mobil", "NYSE"),
    ("CVX", "Chevron", "NYSE"),
    ("OXY", "Occidental Petroleum", "NYSE"),
    ("SLB", "Schlumberger", "NYSE"),
    # Defense
    ("LMT", "Lockheed Martin", "NYSE"),
    ("RTX", "RTX Corp", "NYSE"),
    ("GD", "General Dynamics", "NYSE"),
    # Healthcare / Bio
    ("LLY", "Eli Lilly", "NYSE"),
    ("UNH", "UnitedHealth", "NYSE"),
    ("ABBV", "AbbVie", "NYSE"),
    ("MRNA", "Moderna", "NASDAQ"),
    # Finance
    ("JPM", "JPMorgan Chase", "NYSE"),
    ("GS", "Goldman Sachs", "NYSE"),
    ("V", "Visa", "NYSE"),
    # Consumer
    ("COST", "Costco", "NASDAQ"),
    ("NKE", "Nike", "NYSE"),
    ("SBUX", "Starbucks", "NASDAQ"),
    # Industrial
    ("CAT", "Caterpillar", "NYSE"),
    ("BA", "Boeing", "NYSE"),
    ("UPS", "UPS", "NYSE"),
    # Mid-cap / Growth
    ("CRWD", "CrowdStrike", "NASDAQ"),
    ("DDOG", "Datadog", "NASDAQ"),
    ("NET", "Cloudflare", "NYSE"),
    ("RKLB", "Rocket Lab", "NASDAQ"),
    ("IONQ", "IonQ", "NYSE"),
]


def _calc_rsi(closes: list[float], period: int = 14) -> float | None:
    """Calculate RSI from a list of closing prices."""
    if len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    recent = deltas[-(period):]
    gains = [d for d in recent if d > 0]
    losses = [-d for d in recent if d < 0]
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _calc_macd_signal(closes: list[float]) -> str:
    """Calculate MACD crossover status from closing prices."""
    if len(closes) < 35:
        return "neutral"

    def _ema(data: list[float], span: int) -> list[float]:
        multiplier = 2 / (span + 1)
        result = [data[0]]
        for val in data[1:]:
            result.append(val * multiplier + result[-1] * (1 - multiplier))
        return result

    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal_line = _ema(macd_line, 9)

    if len(macd_line) < 2 or len(signal_line) < 2:
        return "neutral"

    curr_diff = macd_line[-1] - signal_line[-1]
    prev_diff = macd_line[-2] - signal_line[-2]

    if prev_diff <= 0 < curr_diff:
        return "bullish_cross"
    if prev_diff >= 0 > curr_diff:
        return "bearish_cross"
    return "neutral"


def _safe_float(val: object) -> float | None:
    """Safely convert a value to float, returning None on failure."""
    if val is None:
        return None
    try:
        result = float(val)  # type: ignore[arg-type]
        if math.isnan(result) or math.isinf(result):
            return None
        return result
    except (TypeError, ValueError):
        return None


def _screen_one(ticker_str: str, name: str, market: str) -> ScreenedStock | None:
    """Screen a single stock. Returns None on failure."""
    try:
        stock = yf.Ticker(ticker_str)
        info = stock.info or {}

        # Skip if no valid price data
        current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
        if current_price is None or current_price <= 0:
            return None

        prev_close = _safe_float(
            info.get("previousClose") or info.get("regularMarketPreviousClose")
        )
        if prev_close is None or prev_close <= 0:
            prev_close = current_price

        change_pct = ((current_price - prev_close) / prev_close) * 100

        # Volume
        volume = int(info.get("volume") or info.get("regularMarketVolume") or 0)
        avg_volume = int(info.get("averageVolume") or 1)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0

        # 52-week
        w52_high = _safe_float(info.get("fiftyTwoWeekHigh")) or current_price
        w52_low = _safe_float(info.get("fiftyTwoWeekLow")) or current_price
        pct_from_high = ((current_price - w52_high) / w52_high) * 100 if w52_high else 0
        pct_from_low = ((current_price - w52_low) / w52_low) * 100 if w52_low else 0

        # Technicals from history
        hist = stock.history(period="6mo")
        closes = hist["Close"].tolist() if not hist.empty else []

        rsi = _calc_rsi(closes) if len(closes) >= 15 else None
        macd_sig = _calc_macd_signal(closes) if len(closes) >= 35 else "neutral"

        sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        sma_200 = _safe_float(info.get("twoHundredDayAverage"))

        return ScreenedStock(
            ticker=ticker_str,
            name=name,
            market=market,
            sector=str(info.get("sector", "")),
            industry=str(info.get("industry", "")),
            current_price=round(current_price, 2),
            prev_close=round(prev_close, 2),
            change_pct=round(change_pct, 2),
            volume=volume,
            avg_volume=avg_volume,
            volume_ratio=round(volume_ratio, 2),
            week_52_high=round(w52_high, 2),
            week_52_low=round(w52_low, 2),
            pct_from_52w_high=round(pct_from_high, 1),
            pct_from_52w_low=round(pct_from_low, 1),
            rsi_14=round(rsi, 1) if rsi is not None else None,
            macd_signal=macd_sig,
            sma_50=round(sma_50, 2) if sma_50 else None,
            sma_200=round(sma_200, 2) if sma_200 else None,
            above_sma_50=current_price > sma_50 if sma_50 else None,
            above_sma_200=current_price > sma_200 if sma_200 else None,
            market_cap=_safe_float(info.get("marketCap")) or 0,
            pe_ratio=_safe_float(info.get("trailingPE")),
            forward_pe=_safe_float(info.get("forwardPE")),
            pb_ratio=_safe_float(info.get("priceToBook")),
            peg_ratio=_safe_float(info.get("pegRatio")),
            roe=_safe_float(info.get("returnOnEquity")),
            debt_to_equity=_safe_float(info.get("debtToEquity")),
            profit_margin=_safe_float(info.get("profitMargins")),
            revenue_growth=_safe_float(info.get("revenueGrowth")),
            earnings_growth=_safe_float(info.get("earningsGrowth")),
            dividend_yield=_safe_float(info.get("dividendYield")),
            free_cashflow=_safe_float(info.get("freeCashflow")),
            beta=_safe_float(info.get("beta")),
        )
    except Exception:  # pylint: disable=broad-exception-caught
        logger.warning("Failed to screen %s", ticker_str)
        return None


class ScreenStocks:
    """Screen a universe of stocks with fundamental + technical data."""

    def execute(self) -> ScreeningResult:
        """Screen all stocks in the universe."""
        result = ScreeningResult()

        logger.info("Screening %d Korean stocks...", len(KR_TICKERS))
        for ticker, name, market in KR_TICKERS:
            screened = _screen_one(ticker, name, market)
            if screened:
                result.kr_stocks.append(screened)
            else:
                result.screening_errors += 1

        logger.info("Screening %d US stocks...", len(US_TICKERS))
        for ticker, name, market in US_TICKERS:
            screened = _screen_one(ticker, name, market)
            if screened:
                result.us_stocks.append(screened)
            else:
                result.screening_errors += 1

        logger.info(
            "Screening complete: %d KR, %d US, %d errors",
            len(result.kr_stocks),
            len(result.us_stocks),
            result.screening_errors,
        )
        return result
