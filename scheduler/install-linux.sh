#!/bin/bash
set -euo pipefail

# ============================================================
# Daily Scheduler - Install Linux cron Job
# ============================================================
# Reads SCHEDULE_TIME from .env (default: 07:30)
# Converts KST target time to local system timezone automatically.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"
CRON_MARKER="# daily-scheduler"

echo "=== Daily Scheduler - Linux Installer ==="
echo ""

# Read SCHEDULE_TIME from .env (format: HH:MM, in KST)
SCHEDULE_TIME="07:30"
if [ -f "$ENV_FILE" ]; then
    FOUND=$(grep -E '^SCHEDULE_TIME=' "$ENV_FILE" | tail -1 | cut -d'=' -f2 | sed 's/#.*//' | tr -d '"' | tr -d "'" | xargs)
    if [ -n "$FOUND" ]; then
        SCHEDULE_TIME="$FOUND"
    fi
fi

KST_HOUR="${SCHEDULE_TIME%%:*}"
KST_MINUTE="${SCHEDULE_TIME##*:}"
# Remove leading zeros for arithmetic
KST_HOUR=$((10#$KST_HOUR))
KST_MINUTE=$((10#$KST_MINUTE))

echo "Target time: ${KST_HOUR}:$(printf '%02d' $KST_MINUTE) KST (from .env SCHEDULE_TIME)"

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

# Remove existing daily-scheduler cron entry
EXISTING_CRON=$(crontab -l 2>/dev/null || true)
NEW_CRON=$(echo "$EXISTING_CRON" | grep -v "$CRON_MARKER" || true)

# Add new cron entry
CRON_LINE="$MINUTE $HOUR * * * /bin/bash $PROJECT_DIR/scheduler/run_daily.sh $CRON_MARKER"
if [ -n "$NEW_CRON" ]; then
    NEW_CRON="$NEW_CRON
$CRON_LINE"
else
    NEW_CRON="$CRON_LINE"
fi

echo "$NEW_CRON" | crontab -

# Make run script executable
chmod +x "$SCRIPT_DIR/run_daily.sh"

# Create log directory
mkdir -p "$PROJECT_DIR/logs"

# Verify
echo ""
if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
    echo "Scheduler installed successfully!"
    echo "   Schedule: Every day at ${HOUR}:$(printf '%02d' $MINUTE) $SYSTEM_TZ (= ${KST_HOUR}:$(printf '%02d' $KST_MINUTE) KST)"
    echo "   Cron entry: $CRON_LINE"
    echo ""
    echo "   To change schedule: edit SCHEDULE_TIME in .env, then re-run this script"
    echo ""
    echo "Commands:"
    echo "   Run now:    make scheduler-linux-start"
    echo "   Uninstall:  make scheduler-linux-uninstall"
    echo "   View logs:  tail -f $PROJECT_DIR/logs/scheduler.log"
else
    echo "Failed to install scheduler. Check cron service status."
    exit 1
fi
