import Link from "next/link";
import { FileText } from "lucide-react";
import type { ReportSummary } from "@/types";
import { formatDate, statusBgColor, formatPercent } from "@/lib/utils";

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
            {report.title}
          </h3>
          <p className="text-xs text-[var(--text-secondary)]">
            {formatDate(report.date)}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {report.win_rate !== null && (
          <span className="text-sm font-medium text-[var(--text-secondary)]">
            {formatPercent(report.win_rate)}
          </span>
        )}
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusBgColor(report.status)}`}
        >
          {report.status}
        </span>
      </div>
    </Link>
  );
}
