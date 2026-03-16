import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { api } from "@/lib/api-client";
import type { ReportDetail } from "@/types";
import {
  formatDate,
  formatPercent,
  statusBgColor,
} from "@/lib/utils";
import RecommendationTable from "@/components/features/recommendation-table";
import ReportHtmlViewer from "./report-html-viewer";
import SectionContent from "./section-content";

interface ReportDetailPageProps {
  params: Promise<{ id: string }>;
}

async function getReport(id: string): Promise<ReportDetail | null> {
  try {
    return await api.get<ReportDetail>(`/api/reports/${id}`);
  } catch {
    return null;
  }
}

export default async function ReportDetailPage({
  params,
}: ReportDetailPageProps) {
  const { id } = await params;
  const report = await getReport(id);

  if (!report) {
    return (
      <div className="space-y-6">
        <Link
          href="/reports"
          className="inline-flex items-center gap-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
        >
          <ArrowLeft size={16} />
          Back to Reports
        </Link>
        <div className="card flex flex-col items-center justify-center py-16">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            Report not found
          </h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            This report may have been removed or does not exist.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/reports"
        className="inline-flex items-center gap-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
      >
        <ArrowLeft size={16} />
        Back to Reports
      </Link>

      {/* Report header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-[var(--text-primary)]">
              {report.title}
            </h1>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              {formatDate(report.date)}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {report.win_rate !== null && (
              <span className="text-lg font-bold text-emerald-400">
                {formatPercent(report.win_rate)}
              </span>
            )}
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${statusBgColor(report.status)}`}
            >
              {report.status}
            </span>
          </div>
        </div>
      </div>

      {/* HTML report viewer */}
      {report.html_path && (
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              Full Report
            </h2>
            <a
              href={`/api/reports/${report.id}/html`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300"
            >
              Open in new tab
              <ExternalLink size={14} />
            </a>
          </div>
          <ReportHtmlViewer reportId={report.id} />
        </div>
      )}

      {/* Sections */}
      {report.sections.length > 0 && (
        <div className="space-y-4">
          {report.sections.map((section, i) => (
            <div key={i} className="card">
              <h2 className="mb-3 text-lg font-semibold text-[var(--text-primary)]">
                {section.title}
              </h2>
              <SectionContent html={section.content} />
            </div>
          ))}
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <div className="card">
          <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
            Recommendations
          </h2>
          <RecommendationTable recommendations={report.recommendations} />
        </div>
      )}
    </div>
  );
}
