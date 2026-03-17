#!/bin/bash
set -euo pipefail

# ============================================================
# Daily Scheduler - Uninstall Linux cron Job
# ============================================================

CRON_MARKER="# daily-scheduler"

echo "=== Daily Scheduler - Linux Uninstaller ==="
echo ""

EXISTING_CRON=$(crontab -l 2>/dev/null || true)

if echo "$EXISTING_CRON" | grep -q "$CRON_MARKER"; then
    NEW_CRON=$(echo "$EXISTING_CRON" | grep -v "$CRON_MARKER" || true)
    if [ -n "$NEW_CRON" ]; then
        echo "$NEW_CRON" | crontab -
    else
        crontab -r 2>/dev/null || true
    fi
    echo "Scheduler uninstalled."
else
    echo "Scheduler is not installed."
fi
