"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { DailyCheck } from "@/types";
import { formatDate } from "@/lib/utils";

interface DailyChecksProps {
  checks: DailyCheck[];
}

export default function DailyChecks({ checks }: DailyChecksProps) {
  const [expandedDate, setExpandedDate] = useState<string | null>(null);

  if (checks.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
        No daily checks available yet.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {checks.map((check) => {
        const isExpanded = expandedDate === check.report_date;
        const total = check.recommendations_checked;
        const accuracy =
          total > 0 ? (check.targets_hit / total) * 100 : 0;

        return (
          <div
            key={check.id}
            className="rounded-lg border border-[var(--border-color)]"
          >
            <button
              onClick={() =>
                setExpandedDate(isExpanded ? null : check.report_date)
              }
              className="flex w-full items-center justify-between p-4 text-left"
            >
              <div className="flex items-center gap-3">
                {isExpanded ? (
                  <ChevronDown size={16} />
                ) : (
                  <ChevronRight size={16} />
                )}
                <span className="font-medium text-[var(--text-primary)]">
                  {formatDate(check.report_date)}
                </span>
              </div>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  accuracy >= 60
                    ? "bg-emerald-500/20 text-emerald-400"
                    : accuracy >= 40
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-red-500/20 text-red-400"
                }`}
              >
                {Math.round(accuracy)}% accuracy
              </span>
            </button>

            {isExpanded && (
              <div className="border-t border-[var(--border-color)] p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-xs font-medium uppercase text-[var(--text-secondary)]">
                      Checked
                    </p>
                    <p className="text-lg font-bold text-[var(--text-primary)]">
                      {check.recommendations_checked}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase text-[var(--text-secondary)]">
                      Targets Hit
                    </p>
                    <p className="text-lg font-bold text-emerald-400">
                      {check.targets_hit}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase text-[var(--text-secondary)]">
                      Stops Hit
                    </p>
                    <p className="text-lg font-bold text-red-400">
                      {check.stops_hit}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase text-[var(--text-secondary)]">
                      Expired
                    </p>
                    <p className="text-lg font-bold text-yellow-400">
                      {check.expired_count}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
