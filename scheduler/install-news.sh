#!/bin/bash
set -euo pipefail

# ============================================================
# Daily Scheduler - Install macOS launchd Job (News Briefing)
# ============================================================
# Reads NEWS_SCHEDULE_TIME from .env (default: 07:15)
# Converts KST target time to local system timezone automatically.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_TEMPLATE="$SCRIPT_DIR/com.dailyscheduler.news.plist"
PLIST_NAME="com.dailyscheduler.news.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"
ENV_FILE="$PROJECT_DIR/.env"

echo "=== Daily Scheduler - News Briefing Installer ==="
echo ""

# Read NEWS_SCHEDULE_TIME from .env (format: HH:MM, in KST)
SCHEDULE_TIME="07:15"
if [ -f "$ENV_FILE" ]; then
    FOUND=$(grep -E '^NEWS_SCHEDULE_TIME=' "$ENV_FILE" | tail -1 | cut -d'=' -f2 | sed 's/#.*//' | tr -d '"' | tr -d "'" | xargs)
    if [ -n "$FOUND" ]; then
        SCHEDULE_TIME="$FOUND"
    fi
fi

KST_HOUR="${SCHEDULE_TIME%%:*}"
KST_MINUTE="${SCHEDULE_TIME##*:}"
# Remove leading zeros for arithmetic
KST_HOUR=$((10#$KST_HOUR))
KST_MINUTE=$((10#$KST_MINUTE))

echo "Target time: ${KST_HOUR}:$(printf '%02d' $KST_MINUTE) KST (from .env NEWS_SCHEDULE_TIME)"

# Convert KST time to local system timezone
# KST = UTC+9
SYSTEM_UTC_OFFSET=$(date +%z)  # e.g., +0900, -0500
OFFSET_SIGN="${SYSTEM_UTC_OFFSET:0:1}"
OFFSET_HH=$((10#${SYSTEM_UTC_OFFSET:1:2}))
if [ "$OFFSET_SIGN" = "-" ]; then
    LOCAL_OFFSET_H=$(( -OFFSET_HH ))
else
    LOCAL_OFFSET_H=$OFFSET_HH
fi
KST_OFFSET_H=9

DIFF_H=$(( LOCAL_OFFSET_H - KST_OFFSET_H ))
TOTAL_MINUTES=$(( (KST_HOUR + DIFF_H) * 60 + KST_MINUTE ))
# Normalize to 0-1439 (minutes in a day)
TOTAL_MINUTES=$(( (TOTAL_MINUTES % 1440 + 1440) % 1440 ))

HOUR=$(( TOTAL_MINUTES / 60 ))
MINUTE=$(( TOTAL_MINUTES % 60 ))

SYSTEM_TZ=$(date +%Z)
echo "Local time: ${HOUR}:$(printf '%02d' $MINUTE) $SYSTEM_TZ"
echo ""

# Unload existing job if present
if launchctl list | grep -q "com.dailyscheduler.news"; then
    echo "Unloading existing job..."
    launchctl bootout "gui/$(id -u)/com.dailyscheduler.news" 2>/dev/null || true
fi

# Generate plist from template
echo "Generating plist..."
sed -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    -e "s|__HOUR__|$HOUR|g" \
    -e "s|__MINUTE__|$MINUTE|g" \
    "$PLIST_TEMPLATE" > "$PLIST_DEST"

# Make run script executable
chmod +x "$SCRIPT_DIR/run_news.sh"

# Create log directory
mkdir -p "$PROJECT_DIR/logs"

# Load the job
echo "Loading launchd job..."
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST"

# Verify
echo ""
if launchctl list | grep -q "com.dailyscheduler.news"; then
    echo "✅ News briefing scheduler installed successfully!"
    echo "   Job: com.dailyscheduler.news"
    echo "   Schedule: Every day at ${HOUR}:$(printf '%02d' $MINUTE) $SYSTEM_TZ (= ${KST_HOUR}:$(printf '%02d' $KST_MINUTE) KST)"
    echo "   Plist: $PLIST_DEST"
    echo ""
    echo "   To change schedule: edit NEWS_SCHEDULE_TIME in .env, then re-run this script"
    echo ""
    echo "Commands:"
    echo "   Start now:  launchctl start com.dailyscheduler.news"
    echo "   Unload:     launchctl bootout gui/\$(id -u)/com.dailyscheduler.news"
    echo "   View logs:  tail -f $PROJECT_DIR/logs/scheduler.log"
else
    echo "❌ Failed to install news briefing scheduler. Check the logs."
    exit 1
fi
