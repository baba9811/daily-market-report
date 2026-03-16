import { RotateCcw } from "lucide-react";
import { api } from "@/lib/api-client";
import type { RetrospectiveData } from "@/types";
import { formatDate } from "@/lib/utils";
import DailyChecks from "./daily-checks";

async function getRetrospective(): Promise<RetrospectiveData | null> {
  try {
    return await api.get<RetrospectiveData>("/api/retrospective");
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
                key={week.week_start}
                className="rounded-lg border border-[var(--border-color)] p-4"
              >
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="font-medium text-[var(--text-primary)]">
                    {formatDate(week.week_start)} -{" "}
                    {formatDate(week.week_end)}
                  </h3>
                  <span
                    className={`text-sm font-bold ${
                      week.avg_accuracy >= 0.6
                        ? "text-emerald-400"
                        : week.avg_accuracy >= 0.4
                          ? "text-yellow-400"
                          : "text-red-400"
                    }`}
                  >
                    {Math.round(week.avg_accuracy * 100)}% avg accuracy
                  </span>
                </div>

                {week.top_sectors.length > 0 && (
                  <div className="mb-2">
                    <span className="text-xs text-[var(--text-secondary)]">
                      Top sectors:{" "}
                    </span>
                    {week.top_sectors.map((sector) => (
                      <span
                        key={sector}
                        className="mr-2 inline-block rounded bg-blue-500/20 px-2 py-0.5 text-xs text-blue-400"
                      >
                        {sector}
                      </span>
                    ))}
                  </div>
                )}

                {week.improvements.length > 0 && (
                  <div>
                    <span className="text-xs text-[var(--text-secondary)]">
                      Improvements:
                    </span>
                    <ul className="mt-1 list-inside list-disc text-sm text-[var(--text-secondary)]">
                      {week.improvements.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
