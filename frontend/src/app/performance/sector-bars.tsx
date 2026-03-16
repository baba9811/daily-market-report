"use client";

import type { SectorPerformance } from "@/types";

interface SectorBarsProps {
  sectors: SectorPerformance[];
}

export default function SectorBars({ sectors }: SectorBarsProps) {
  if (sectors.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
        No sector data available yet.
      </p>
    );
  }

  const maxWinRate = Math.max(...sectors.map((s) => s.win_rate));

  return (
    <div className="space-y-4">
      {sectors.map((sector) => (
        <div key={sector.sector} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-[var(--text-primary)]">
              {sector.sector}
            </span>
            <div className="flex items-center gap-4 text-[var(--text-secondary)]">
              <span>Win: {Math.round(sector.win_rate)}%</span>
              <span>
                Avg Return:{" "}
                <span
                  className={
                    sector.avg_return >= 0
                      ? "text-emerald-400"
                      : "text-red-400"
                  }
                >
                  {sector.avg_return >= 0 ? "+" : ""}
                  {sector.avg_return.toFixed(1)}%
                </span>
              </span>
              <span className="text-xs">({sector.count} picks)</span>
            </div>
          </div>
          <div className="h-2 w-full rounded-full bg-[var(--bg-hover)]">
            <div
              className="h-2 rounded-full bg-blue-500"
              style={{
                width: `${maxWinRate > 0 ? (sector.win_rate / maxWinRate) * 100 : 0}%`,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
