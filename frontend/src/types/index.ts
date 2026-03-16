/** Shared TypeScript types for the Daily Scheduler frontend. */

export interface DashboardStats {
  total_reports: number;
  success_rate: number;
  avg_win_rate: number;
  latest_report_date: string | null;
  alerts: Alert[];
}

export interface Alert {
  level: "info" | "warning" | "error";
  message: string;
  timestamp: string;
}

export interface ReportSummary {
  id: number;
  date: string;
  title: string;
  status: "success" | "failure" | "pending";
  win_rate: number | null;
  created_at: string;
}

export interface ReportDetail {
  id: number;
  date: string;
  title: string;
  status: "success" | "failure" | "pending";
  win_rate: number | null;
  html_path: string | null;
  sections: ReportSection[];
  recommendations: Recommendation[];
  created_at: string;
}

export interface ReportSection {
  title: string;
  content: string;
}

export interface Recommendation {
  ticker: string;
  name: string;
  sector: string;
  action: "buy" | "sell" | "hold";
  confidence: number;
  reason: string;
}

export interface PerformanceData {
  dates: string[];
  win_rates: number[];
  cumulative_returns: number[];
  sector_performance: SectorPerformance[];
  recent_recommendations: Recommendation[];
}

export interface SectorPerformance {
  sector: string;
  win_rate: number;
  avg_return: number;
  count: number;
}

export interface RetrospectiveDay {
  date: string;
  predicted: string[];
  actual: string[];
  accuracy: number;
  notes: string;
}

export interface WeeklyAnalysis {
  week_start: string;
  week_end: string;
  avg_accuracy: number;
  top_sectors: string[];
  improvements: string[];
}

export interface RetrospectiveData {
  daily_checks: RetrospectiveDay[];
  weekly_analyses: WeeklyAnalysis[];
}

export interface SettingsData {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  email_from: string;
  email_to: string[];
  claude_model: string;
  report_language: string;
}

export interface SystemStatus {
  database: boolean;
  claude_cli: boolean;
  smtp: boolean;
  last_run: string | null;
  next_run: string | null;
}

export interface PipelineStatus {
  running: boolean;
  last_result: "success" | "failure" | null;
  last_run: string | null;
}
