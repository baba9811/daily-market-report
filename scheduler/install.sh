#!/bin/bash
set -euo pipefail

# ============================================================
# Daily Scheduler - Install macOS launchd Job
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_TEMPLATE="$SCRIPT_DIR/com.dailyscheduler.report.plist"
PLIST_NAME="com.dailyscheduler.report.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== Daily Scheduler - Installer ==="
echo ""

# Detect timezone and calculate hour
SYSTEM_TZ=$(date +%Z)
echo "System timezone: $SYSTEM_TZ"

# Default: 7:30 AM KST
# KST = UTC+9
HOUR=7
case "$SYSTEM_TZ" in
    KST|JST)
        HOUR=7
        ;;
    UTC|GMT)
        HOUR=22  # 22:30 UTC = 07:30 KST (next day)
        ;;
    PST|PDT)
        HOUR=14  # 14:30 PST = 07:30 KST (next day)
        ;;
    EST|EDT)
        HOUR=17  # 17:30 EST = 07:30 KST (next day)
        ;;
    CST|CDT)
        HOUR=16  # 16:30 CST = 07:30 KST (next day)
        ;;
    *)
        echo "Unknown timezone: $SYSTEM_TZ"
        echo "Defaulting to Hour=7. You may need to adjust manually."
        HOUR=7
        ;;
esac

echo "Scheduled hour: ${HOUR}:30 ($SYSTEM_TZ) = 07:30 KST"
echo ""

# Unload existing job if present
if launchctl list | grep -q "com.dailyscheduler.report"; then
    echo "Unloading existing job..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Generate plist from template
echo "Generating plist..."
sed -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    -e "s|__HOUR__|$HOUR|g" \
    "$PLIST_TEMPLATE" > "$PLIST_DEST"

# Make run script executable
chmod +x "$SCRIPT_DIR/run_daily.sh"

# Create log directory
mkdir -p "$PROJECT_DIR/logs"

# Load the job
echo "Loading launchd job..."
launchctl load "$PLIST_DEST"

# Verify
echo ""
if launchctl list | grep -q "com.dailyscheduler.report"; then
    echo "✅ Scheduler installed successfully!"
    echo "   Job: com.dailyscheduler.report"
    echo "   Schedule: Every day at ${HOUR}:30 $SYSTEM_TZ (07:30 KST)"
    echo "   Plist: $PLIST_DEST"
    echo ""
    echo "Commands:"
    echo "   Start now:  launchctl start com.dailyscheduler.report"
    echo "   Unload:     launchctl unload $PLIST_DEST"
    echo "   View logs:  tail -f $PROJECT_DIR/logs/scheduler.log"
else
    echo "❌ Failed to install scheduler. Check the logs."
    exit 1
fi
