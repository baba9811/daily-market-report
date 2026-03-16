"""MarketContext entity — real-time market data snapshot for report generation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IndexData:
    """A single market index snapshot."""

    name: str
    ticker: str
    price: float
    change_percent: float
    prev_close: float


@dataclass
class FuturesData:
    """US equity futures snapshot."""

    name: str
    ticker: str
    price: float
    change_percent: float


@dataclass
class SectorETFData:
    """Sector ETF with change and volume data."""

    name: str
    ticker: str
    price: float
    change_percent: float
    volume: int = 0


@dataclass
class MarketContext:
    """Aggregated market data to anchor report generation with real prices."""

    indices: list[IndexData] = field(default_factory=list)
    fx_rates: dict[str, float] = field(default_factory=dict)
    commodities: dict[str, float] = field(default_factory=dict)
    futures: list[FuturesData] = field(default_factory=list)
    vix: float | None = None
    sector_etfs: list[SectorETFData] = field(default_factory=list)

    def to_prompt_text(self) -> str:
        """Format market data as text for inclusion in the prompt."""
        if not self.indices and not self.fx_rates and not self.commodities:
            return "No market data available."

        lines: list[str] = []
        self._fmt_indices(lines)
        self._fmt_futures(lines)
        self._fmt_vix(lines)
        self._fmt_fx(lines)
        self._fmt_commodities(lines)
        self._fmt_sector_etfs(lines)
        return "\n".join(lines)

    def _fmt_indices(self, lines: list[str]) -> None:
        if not self.indices:
            return
        lines.append("### Major Indices")
        lines.append("| Index | Price | Change (%) |")
        lines.append("|-------|------:|----------:|")
        for idx in self.indices:
            sign = "+" if idx.change_percent >= 0 else ""
            lines.append(f"| {idx.name} | {idx.price:,.2f} | {sign}{idx.change_percent:.2f}% |")
        lines.append("")

    def _fmt_futures(self, lines: list[str]) -> None:
        if not self.futures:
            return
        lines.append("### US Equity Futures")
        lines.append("| Futures | Price | Change (%) |")
        lines.append("|---------|------:|----------:|")
        for f in self.futures:
            sign = "+" if f.change_percent >= 0 else ""
            lines.append(f"| {f.name} | {f.price:,.2f} | {sign}{f.change_percent:.2f}% |")
        lines.append("")

    def _fmt_vix(self, lines: list[str]) -> None:
        if self.vix is None:
            return
        lines.append(f"### Volatility: VIX = {self.vix:.2f}")
        if self.vix >= 30:
            lines.append("⚠ VIX ≥ 30: Extreme fear / high volatility regime")
        elif self.vix >= 20:
            lines.append("⚡ VIX 20-30: Elevated volatility")
        else:
            lines.append("✅ VIX < 20: Low volatility / complacency")
        lines.append("")

    def _fmt_fx(self, lines: list[str]) -> None:
        if not self.fx_rates:
            return
        lines.append("### FX Rates")
        for pair, rate in self.fx_rates.items():
            lines.append(f"- {pair}: {rate:,.2f}")
        lines.append("")

    def _fmt_commodities(self, lines: list[str]) -> None:
        if not self.commodities:
            return
        lines.append("### Commodities")
        for name, price in self.commodities.items():
            lines.append(f"- {name}: ${price:,.2f}")
        lines.append("")

    def _fmt_sector_etfs(self, lines: list[str]) -> None:
        if not self.sector_etfs:
            return
        lines.append("### Sector ETF Performance")
        lines.append("| Sector | Ticker | Price | Change (%) | Volume |")
        lines.append("|--------|--------|------:|----------:|-------:|")
        for s in self.sector_etfs:
            sign = "+" if s.change_percent >= 0 else ""
            lines.append(
                f"| {s.name} | {s.ticker} | {s.price:,.2f}"
                f" | {sign}{s.change_percent:.2f}% | {s.volume:,} |"
            )
        lines.append("")
