import type { RecommendationOut } from "@/types";
import { cn } from "@/lib/utils";

interface RecommendationTableProps {
  recommendations: RecommendationOut[];
}

export default function RecommendationTable({
  recommendations,
}: RecommendationTableProps) {
  if (recommendations.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
        No recommendations available yet.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-[var(--border-color)]">
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Ticker
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Name
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Direction
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Entry / Target / Stop
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Status
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              P&L
            </th>
          </tr>
        </thead>
        <tbody>
          {recommendations.map((rec) => (
            <tr
              key={rec.id}
              className="border-b border-[var(--border-color)] last:border-b-0"
            >
              <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                {rec.ticker}
              </td>
              <td className="px-4 py-3 text-[var(--text-primary)]">
                {rec.name}
              </td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    rec.direction === "LONG" &&
                      "bg-emerald-500/20 text-emerald-400",
                    rec.direction === "SHORT" &&
                      "bg-red-500/20 text-red-400"
                  )}
                >
                  {rec.direction}
                </span>
              </td>
              <td className="px-4 py-3 text-xs text-[var(--text-secondary)]">
                {rec.entry_price.toLocaleString()} / {rec.target_price.toLocaleString()} / {rec.stop_loss.toLocaleString()}
              </td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    rec.status === "OPEN" &&
                      "bg-blue-500/20 text-blue-400",
                    rec.status === "TARGET_HIT" &&
                      "bg-emerald-500/20 text-emerald-400",
                    rec.status === "STOP_HIT" &&
                      "bg-red-500/20 text-red-400",
                    rec.status === "EXPIRED" &&
                      "bg-yellow-500/20 text-yellow-400"
                  )}
                >
                  {rec.status}
                </span>
              </td>
              <td
                className={cn(
                  "px-4 py-3 text-sm font-medium",
                  rec.pnl_percent !== null && rec.pnl_percent > 0
                    ? "text-emerald-400"
                    : "text-red-400"
                )}
              >
                {rec.pnl_percent !== null
                  ? `${rec.pnl_percent > 0 ? "+" : ""}${rec.pnl_percent.toFixed(2)}%`
                  : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
