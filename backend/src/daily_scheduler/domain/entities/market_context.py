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
class MarketContext:
    """Aggregated market data to anchor report generation with real prices."""

    indices: list[IndexData] = field(default_factory=list)
    fx_rates: dict[str, float] = field(default_factory=dict)
    commodities: dict[str, float] = field(default_factory=dict)

    def to_prompt_text(self) -> str:
        """Format market data as text for inclusion in the prompt."""
        if not self.indices and not self.fx_rates and not self.commodities:
            return "No market data available."

        lines: list[str] = []

        if self.indices:
            lines.append("### Major Indices")
            lines.append("| Index | Price | Change (%) |")
            lines.append("|-------|------:|----------:|")
            for idx in self.indices:
                sign = "+" if idx.change_percent >= 0 else ""
                lines.append(f"| {idx.name} | {idx.price:,.2f} | {sign}{idx.change_percent:.2f}% |")
            lines.append("")

        if self.fx_rates:
            lines.append("### FX Rates")
            for pair, rate in self.fx_rates.items():
                lines.append(f"- {pair}: {rate:,.2f}")
            lines.append("")

        if self.commodities:
            lines.append("### Commodities")
            for name, price in self.commodities.items():
                lines.append(f"- {name}: ${price:,.2f}")
            lines.append("")

        return "\n".join(lines)
