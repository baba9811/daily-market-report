import Link from "next/link";
import { FileText } from "lucide-react";
import type { ReportSummary } from "@/types";
import { formatDate } from "@/lib/utils";

interface ReportCardProps {
  report: ReportSummary;
}

export default function ReportCard({ report }: ReportCardProps) {
  return (
    <Link
      href={`/reports/${report.id}`}
      className="card card-hover flex items-center justify-between"
    >
      <div className="flex items-center gap-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/20">
          <FileText size={20} className="text-blue-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            {
              {
                daily: "Daily Report",
                news: "News Briefing",
                global_news: "Global News",
              }[report.report_type] ?? "Weekly Report"
            }{" "}
            —{" "}
            {formatDate(report.report_date)}
          </h3>
          <p className="text-xs text-[var(--text-secondary)] line-clamp-1">
            {report.summary || "No summary available"}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {report.generation_time_s !== null && (
          <span className="text-xs text-[var(--text-secondary)]">
            {report.generation_time_s.toFixed(1)}s
          </span>
        )}
        <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-xs font-medium text-emerald-400">
          {report.report_type}
        </span>
      </div>
    </Link>
  );
}
