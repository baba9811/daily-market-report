import type { Recommendation } from "@/types";
import { cn } from "@/lib/utils";

interface RecommendationTableProps {
  recommendations: Recommendation[];
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
              Sector
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Action
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Confidence
            </th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">
              Reason
            </th>
          </tr>
        </thead>
        <tbody>
          {recommendations.map((rec, i) => (
            <tr
              key={`${rec.ticker}-${i}`}
              className="border-b border-[var(--border-color)] last:border-b-0"
            >
              <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                {rec.ticker}
              </td>
              <td className="px-4 py-3 text-[var(--text-primary)]">
                {rec.name}
              </td>
              <td className="px-4 py-3 text-[var(--text-secondary)]">
                {rec.sector}
              </td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    rec.action === "buy" && "bg-emerald-500/20 text-emerald-400",
                    rec.action === "sell" && "bg-red-500/20 text-red-400",
                    rec.action === "hold" && "bg-yellow-500/20 text-yellow-400"
                  )}
                >
                  {rec.action.toUpperCase()}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-16 rounded-full bg-[var(--bg-hover)]">
                    <div
                      className="h-1.5 rounded-full bg-blue-500"
                      style={{ width: `${rec.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-[var(--text-secondary)]">
                    {Math.round(rec.confidence * 100)}%
                  </span>
                </div>
              </td>
              <td className="max-w-xs truncate px-4 py-3 text-[var(--text-secondary)]">
                {rec.reason}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
