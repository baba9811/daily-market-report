"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import type { RetrospectiveDay } from "@/types";
import { formatDate, cn } from "@/lib/utils";

interface DailyChecksProps {
  checks: RetrospectiveDay[];
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
        const isExpanded = expandedDate === check.date;
        return (
          <div
            key={check.date}
            className="rounded-lg border border-[var(--border-color)]"
          >
            <button
              onClick={() =>
                setExpandedDate(isExpanded ? null : check.date)
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
                  {formatDate(check.date)}
                </span>
              </div>
              <span
                className={cn(
                  "rounded-full px-2.5 py-0.5 text-xs font-medium",
                  check.accuracy >= 0.6
                    ? "bg-emerald-500/20 text-emerald-400"
                    : check.accuracy >= 0.4
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-red-500/20 text-red-400"
                )}
              >
                {Math.round(check.accuracy * 100)}% accuracy
              </span>
            </button>

            {isExpanded && (
              <div className="border-t border-[var(--border-color)] p-4">
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  {/* Predicted */}
                  <div>
                    <h4 className="mb-2 text-xs font-medium uppercase text-[var(--text-secondary)]">
                      Predicted
                    </h4>
                    <div className="space-y-1">
                      {check.predicted.map((item, i) => (
                        <p
                          key={i}
                          className="text-sm text-[var(--text-primary)]"
                        >
                          {item}
                        </p>
                      ))}
                    </div>
                  </div>

                  {/* Actual */}
                  <div>
                    <h4 className="mb-2 text-xs font-medium uppercase text-[var(--text-secondary)]">
                      Actual
                    </h4>
                    <div className="space-y-1">
                      {check.actual.map((item, i) => (
                        <p
                          key={i}
                          className="text-sm text-[var(--text-primary)]"
                        >
                          {item}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>

                {check.notes && (
                  <div className="mt-4 rounded-lg bg-[var(--bg-hover)] p-3">
                    <h4 className="mb-1 text-xs font-medium uppercase text-[var(--text-secondary)]">
                      Notes
                    </h4>
                    <p className="text-sm text-[var(--text-primary)]">
                      {check.notes}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
