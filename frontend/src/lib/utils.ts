/** Helper functions for the Daily Scheduler frontend. */

/**
 * Merge CSS class names, filtering out falsy values.
 */
export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

/**
 * Format a date string to a human-readable format.
 */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a date string to a short format (MM/DD).
 */
export function formatDateShort(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    month: "2-digit",
    day: "2-digit",
  });
}

/**
 * Format a percentage value to a display string.
 * Backend returns values already as percentages (e.g. 65.3 means 65.3%).
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

/**
 * Get a color class based on a status value.
 */
export function statusColor(
  status: "success" | "failure" | "pending"
): string {
  switch (status) {
    case "success":
      return "text-emerald-400";
    case "failure":
      return "text-red-400";
    case "pending":
      return "text-yellow-400";
  }
}

/**
 * Get a background color class based on a status value.
 */
export function statusBgColor(
  status: "success" | "failure" | "pending"
): string {
  switch (status) {
    case "success":
      return "bg-emerald-500/20 text-emerald-400";
    case "failure":
      return "bg-red-500/20 text-red-400";
    case "pending":
      return "bg-yellow-500/20 text-yellow-400";
  }
}

/**
 * Get color for an alert level.
 */
export function alertColor(level: "info" | "warning" | "error"): string {
  switch (level) {
    case "info":
      return "text-blue-400";
    case "warning":
      return "text-yellow-400";
    case "error":
      return "text-red-400";
  }
}
