import { BarChart3 } from "lucide-react";
import { api } from "@/lib/api-client";
import type { PerformanceData } from "@/types";
import RecommendationTable from "@/components/features/recommendation-table";
import PerformanceCharts from "./performance-charts";
import SectorBars from "./sector-bars";

async function getPerformance(): Promise<PerformanceData | null> {
  try {
    return await api.get<PerformanceData>("/api/performance");
  } catch {
    return null;
  }
}

export default async function PerformancePage() {
  const data = await getPerformance();

  if (!data) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            Performance
          </h1>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Track prediction accuracy and returns
          </p>
        </div>
        <div className="card flex flex-col items-center justify-center py-16">
          <BarChart3
            size={48}
            className="mb-4 text-[var(--text-secondary)]"
          />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            No performance data
          </h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Performance data will appear after reports are generated and
            evaluated.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
          Performance
        </h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          Track prediction accuracy and returns
        </p>
      </div>

      {/* Charts */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
          Win Rate & Returns Over Time
        </h2>
        <PerformanceCharts
          dates={data.dates}
          winRates={data.win_rates}
          cumulativeReturns={data.cumulative_returns}
        />
      </div>

      {/* Sector performance */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
          Sector Performance
        </h2>
        <SectorBars sectors={data.sector_performance} />
      </div>

      {/* Recent recommendations */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
          Recent Recommendations
        </h2>
        <RecommendationTable recommendations={data.recent_recommendations} />
      </div>
    </div>
  );
}
