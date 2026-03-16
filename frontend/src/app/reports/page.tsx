import { FileText } from "lucide-react";
import { api } from "@/lib/api-client";
import type { ReportSummary } from "@/types";
import ReportCard from "@/components/ui/report-card";

async function getReports(): Promise<ReportSummary[]> {
  try {
    return await api.get<ReportSummary[]>("/api/reports");
  } catch {
    return [];
  }
}

export default async function ReportsPage() {
  const reports = await getReports();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
          Reports
        </h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          Browse all generated daily reports
        </p>
      </div>

      {/* Report list */}
      {reports.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-16">
          <FileText size={48} className="mb-4 text-[var(--text-secondary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            No reports yet
          </h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Reports will appear here after the pipeline runs.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      )}
    </div>
  );
}
