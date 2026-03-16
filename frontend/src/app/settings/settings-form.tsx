"use client";

import { useState } from "react";
import { Save, Loader2 } from "lucide-react";
import type { SettingsData } from "@/types";
import { api } from "@/lib/api-client";

interface SettingsFormProps {
  initialSettings: SettingsData;
}

export default function SettingsForm({ initialSettings }: SettingsFormProps) {
  const [settings, setSettings] = useState<SettingsData>(initialSettings);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  function handleChange(field: keyof SettingsData, value: string | number) {
    setSettings((prev) => ({ ...prev, [field]: value }));
    setMessage(null);
  }

  function handleEmailToChange(value: string) {
    const emails = value
      .split(",")
      .map((e) => e.trim())
      .filter(Boolean);
    setSettings((prev) => ({ ...prev, email_to: emails }));
    setMessage(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await api.put("/api/settings", settings);
      setMessage({ type: "success", text: "Settings saved successfully." });
    } catch {
      setMessage({
        type: "error",
        text: "Failed to save settings. Check the backend connection.",
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Email settings */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">
          Email Configuration
        </h2>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm text-[var(--text-secondary)]">
              SMTP Host
            </label>
            <input
              type="text"
              value={settings.smtp_host}
              onChange={(e) => handleChange("smtp_host", e.target.value)}
              className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-[var(--text-secondary)]">
              SMTP Port
            </label>
            <input
              type="number"
              value={settings.smtp_port}
              onChange={(e) =>
                handleChange("smtp_port", parseInt(e.target.value, 10) || 0)
              }
              className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm text-[var(--text-secondary)]">
            SMTP User
          </label>
          <input
            type="text"
            value={settings.smtp_user}
            onChange={(e) => handleChange("smtp_user", e.target.value)}
            className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-[var(--text-secondary)]">
            From Address
          </label>
          <input
            type="email"
            value={settings.email_from}
            onChange={(e) => handleChange("email_from", e.target.value)}
            className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-[var(--text-secondary)]">
            Recipients (comma-separated)
          </label>
          <input
            type="text"
            value={settings.email_to.join(", ")}
            onChange={(e) => handleEmailToChange(e.target.value)}
            className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none focus:border-blue-500"
            placeholder="user@example.com, other@example.com"
          />
        </div>
      </div>

      {/* Claude settings */}
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">
          AI Model
        </h2>

        <div>
          <label className="mb-1 block text-sm text-[var(--text-secondary)]">
            Claude Model
          </label>
          <select
            value={settings.claude_model}
            onChange={(e) => handleChange("claude_model", e.target.value)}
            className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none focus:border-blue-500"
          >
            <option value="sonnet">Claude Sonnet</option>
            <option value="opus">Claude Opus</option>
            <option value="haiku">Claude Haiku</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm text-[var(--text-secondary)]">
            Report Language
          </label>
          <select
            value={settings.report_language}
            onChange={(e) =>
              handleChange("report_language", e.target.value)
            }
            className="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none focus:border-blue-500"
          >
            <option value="en">English</option>
            <option value="ko">Korean</option>
            <option value="ja">Japanese</option>
          </select>
        </div>
      </div>

      {/* Save button */}
      <div className="flex items-center gap-4">
        <button
          type="submit"
          disabled={saving}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Save size={16} />
          )}
          {saving ? "Saving..." : "Save Settings"}
        </button>

        {message && (
          <p
            className={`text-sm ${
              message.type === "success"
                ? "text-emerald-400"
                : "text-red-400"
            }`}
          >
            {message.text}
          </p>
        )}
      </div>
    </form>
  );
}
