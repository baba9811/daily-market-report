/**
 * Shared TypeScript types for the Daily Scheduler frontend.
 *
 * All types are derived from the auto-generated OpenAPI spec.
 * Run `make generate-types` to regenerate api.generated.ts.
 */

import type { components } from "./api.generated";

// ─── Dashboard ───────────────────────────────────────────
export type DashboardStats = components["schemas"]["DashboardOut"];
export type DashboardAlert = components["schemas"]["DashboardAlert"];
export type LatestReportInfo = components["schemas"]["LatestReportInfo"];

// ─── Reports ─────────────────────────────────────────────
export type ReportSummary = components["schemas"]["ReportOut"];
export type ReportDetail = components["schemas"]["ReportDetailOut"];

// ─── Performance ─────────────────────────────────────────
export type PerformanceSummary = components["schemas"]["PerformanceSummary"];
export type SectorPerformance = components["schemas"]["SectorPerformance"];
export type TimeseriesPoint = components["schemas"]["TimeseriesPoint"];
export type RecommendationOut = components["schemas"]["RecommendationOut"];

// ─── Retrospective ───────────────────────────────────────
export type WeeklyAnalysis = components["schemas"]["WeeklyAnalysisOut"];
export type DailyCheck = components["schemas"]["DailyCheckOut"];

// ─── Settings ────────────────────────────────────────────
export type SettingsData = components["schemas"]["SettingsOut"];
export type SystemStatus = components["schemas"]["StatusOut"];
export type PipelineStatus = components["schemas"]["PipelineStatusOut"];
export type PipelineRunResult = components["schemas"]["PipelineRunResult"];
