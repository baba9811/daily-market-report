import {
  TrendingUp,
  FileText,
  Target,
  AlertTriangle,
  CheckCircle,
  Info,
} from "lucide-react";
import { api } from "@/lib/api-client";
import type { DashboardStats } from "@/types";
import { formatPercent, formatDate, alertColor } from "@/lib/utils";
import DashboardWinRate from "./dashboard-win-rate";

async function getDashboardStats(): Promise<DashboardStats | null> {
  try {
    return await api.get<DashboardStats>("/api/dashboard/stats");
  } catch {
    return null;
  }
}

export default async function DashboardPage() {
  const stats = await getDashboardStats();

  // Fallback data when API is unavailable
  const data: DashboardStats = stats ?? {
    total_reports: 0,
    success_rate: 0,
    avg_win_rate: 0,
    latest_report_date: null,
    alerts: [],
  };

  const statCards = [
    {
      label: "Total Reports",
      value: data.total_reports.toString(),
      icon: <FileText size={20} className="text-blue-400" />,
      color: "text-blue-400",
    },
    {
      label: "Success Rate",
      value: formatPercent(data.success_rate),
      icon: <CheckCircle size={20} className="text-emerald-400" />,
      color: "text-emerald-400",
    },
    {
      label: "Avg Win Rate",
      value: formatPercent(data.avg_win_rate),
      icon: <Target size={20} className="text-yellow-400" />,
      color: "text-yellow-400",
    },
    {
      label: "Latest Report",
      value: data.latest_report_date
        ? formatDate(data.latest_report_date)
        : "None",
      icon: <TrendingUp size={20} className="text-purple-400" />,
      color: "text-purple-400",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          Overview of your daily report pipeline
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div key={card.label} className="card">
            <div className="flex items-center justify-between">
              <p className="text-sm text-[var(--text-secondary)]">
                {card.label}
              </p>
              {card.icon}
            </div>
            <p className={`mt-2 text-2xl font-bold ${card.color}`}>
              {card.value}
            </p>
          </div>
        ))}
      </div>

      {/* Win rate gauge & alerts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Win rate */}
        <div className="card">
          <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
            Win Rate
          </h2>
          <div className="flex items-center justify-center">
            <DashboardWinRate value={data.avg_win_rate} />
          </div>
        </div>

        {/* Alerts */}
        <div className="card">
          <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
            Alerts
          </h2>
          {data.alerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-[var(--text-secondary)]">
              <CheckCircle size={32} className="mb-2 text-emerald-400" />
              <p className="text-sm">No alerts at this time</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data.alerts.map((alert, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 rounded-lg bg-[var(--bg-hover)] p-3"
                >
                  {alert.level === "error" ? (
                    <AlertTriangle
                      size={16}
                      className={alertColor(alert.level)}
                    />
                  ) : (
                    <Info size={16} className={alertColor(alert.level)} />
                  )}
                  <div>
                    <p
                      className={`text-sm font-medium ${alertColor(alert.level)}`}
                    >
                      {alert.message}
                    </p>
                    <p className="text-xs text-[var(--text-secondary)]">
                      {formatDate(alert.timestamp)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
