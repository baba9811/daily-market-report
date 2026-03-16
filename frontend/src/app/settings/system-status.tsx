"use client";

import { useState } from "react";
import {
  Database,
  Cpu,
  Mail,
  Clock,
  RefreshCw,
  CheckCircle,
  XCircle,
  Play,
  Loader2,
} from "lucide-react";
import type { SystemStatus, PipelineStatus } from "@/types";
import { api } from "@/lib/api-client";
import { formatDate } from "@/lib/utils";

interface SystemStatusPanelProps {
  status: SystemStatus | null;
}

export default function SystemStatusPanel({
  status,
}: SystemStatusPanelProps) {
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(
    null
  );
  const [runningPipeline, setRunningPipeline] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(status);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      const newStatus = await api.get<SystemStatus>("/api/settings/status");
      setCurrentStatus(newStatus);
    } catch {
      // Keep existing status
    } finally {
      setRefreshing(false);
    }
  }

  async function handleRunPipeline() {
    setRunningPipeline(true);
    try {
      const result = await api.post<PipelineStatus>("/api/pipeline/run");
      setPipelineStatus(result);
    } catch {
      setPipelineStatus({
        running: false,
        last_result: "failure",
        last_run: null,
      });
    } finally {
      setRunningPipeline(false);
    }
  }

  const items = currentStatus
    ? [
        {
          label: "Database",
          ok: currentStatus.database,
          icon: <Database size={16} />,
        },
        {
          label: "Claude CLI",
          ok: currentStatus.claude_cli,
          icon: <Cpu size={16} />,
        },
        {
          label: "SMTP",
          ok: currentStatus.smtp,
          icon: <Mail size={16} />,
        },
      ]
    : [];

  return (
    <div className="space-y-4">
      {/* System status */}
      <div className="card">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            System Status
          </h2>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="rounded-lg p-1.5 text-[var(--text-secondary)] transition-colors hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]"
            title="Refresh status"
          >
            <RefreshCw
              size={16}
              className={refreshing ? "animate-spin" : ""}
            />
          </button>
        </div>

        {!currentStatus ? (
          <p className="text-sm text-[var(--text-secondary)]">
            Unable to check system status. Is the backend running?
          </p>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  {item.icon}
                  {item.label}
                </div>
                {item.ok ? (
                  <CheckCircle size={16} className="text-emerald-400" />
                ) : (
                  <XCircle size={16} className="text-red-400" />
                )}
              </div>
            ))}

            {/* Schedule info */}
            {currentStatus.last_run && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  <Clock size={16} />
                  Last Run
                </div>
                <span className="text-xs text-[var(--text-secondary)]">
                  {formatDate(currentStatus.last_run)}
                </span>
              </div>
            )}
            {currentStatus.next_run && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  <Clock size={16} />
                  Next Run
                </div>
                <span className="text-xs text-[var(--text-secondary)]">
                  {formatDate(currentStatus.next_run)}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Manual run */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
          Manual Run
        </h2>
        <p className="mb-4 text-sm text-[var(--text-secondary)]">
          Trigger the daily pipeline manually.
        </p>
        <button
          onClick={handleRunPipeline}
          disabled={runningPipeline}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
        >
          {runningPipeline ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Play size={16} />
          )}
          {runningPipeline ? "Running..." : "Run Pipeline"}
        </button>

        {pipelineStatus && (
          <div className="mt-3 rounded-lg bg-[var(--bg-hover)] p-3">
            <p
              className={`text-sm font-medium ${
                pipelineStatus.last_result === "success"
                  ? "text-emerald-400"
                  : "text-red-400"
              }`}
            >
              Pipeline {pipelineStatus.last_result === "success"
                ? "completed successfully"
                : "failed"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
