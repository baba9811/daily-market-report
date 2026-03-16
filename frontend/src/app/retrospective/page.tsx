import { RotateCcw } from "lucide-react";
import { api } from "@/lib/api-client";
import type { WeeklyAnalysis, DailyCheck } from "@/types";
import { formatDate } from "@/lib/utils";
import DailyChecks from "./daily-checks";

interface RetrospectivePageData {
  daily_checks: DailyCheck[];
  weekly_analyses: WeeklyAnalysis[];
}

async function getRetrospective(): Promise<RetrospectivePageData | null> {
  try {
    const [daily_checks, weekly_analyses] = await Promise.all([
      api.get<DailyCheck[]>("/api/retrospective/daily-checks"),
      api.get<WeeklyAnalysis[]>("/api/retrospective/weekly"),
    ]);
    return { daily_checks, weekly_analyses };
  } catch {
    return null;
  }
}

export default async function RetrospectivePage() {
  const data = await getRetrospective();

  if (!data) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            Retrospective
          </h1>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Review prediction accuracy and learn from results
          </p>
        </div>
        <div className="card flex flex-col items-center justify-center py-16">
          <RotateCcw
            size={48}
            className="mb-4 text-[var(--text-secondary)]"
          />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            No retrospective data
          </h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Retrospective analysis will appear after the pipeline evaluates
            past predictions.
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
          Retrospective
        </h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          Review prediction accuracy and learn from results
        </p>
      </div>

      {/* Daily checks */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
          Daily Accuracy Checks
        </h2>
        <DailyChecks checks={data.daily_checks} />
      </div>

      {/* Weekly analyses */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
          Weekly Analyses
        </h2>
        {data.weekly_analyses.length === 0 ? (
          <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
            No weekly analyses available yet.
          </p>
        ) : (
          <div className="space-y-4">
            {data.weekly_analyses.map((week) => (
              <div
                key={week.id}
                className="rounded-lg border border-[var(--border-color)] p-4"
              >
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="font-medium text-[var(--text-primary)]">
                    {formatDate(week.week_start)} -{" "}
                    {formatDate(week.week_end)}
                  </h3>
                  <span className="text-sm text-[var(--text-secondary)]">
                    {week.win_count}W / {week.loss_count}L
                    {week.avg_return_pct !== null && (
                      <span
                        className={
                          week.avg_return_pct >= 0
                            ? " text-emerald-400"
                            : " text-red-400"
                        }
                      >
                        {" "}
                        ({week.avg_return_pct >= 0 ? "+" : ""}
                        {week.avg_return_pct.toFixed(1)}%)
                      </span>
                    )}
                  </span>
                </div>
                {week.analysis_text && (
                  <p className="text-sm text-[var(--text-secondary)] line-clamp-3">
                    {week.analysis_text}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
