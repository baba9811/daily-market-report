#!/bin/bash
set -euo pipefail

# ============================================================
# Daily Scheduler - Run Daily Pipeline
# Triggered by macOS launchd or manually
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/scheduler.log"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "===== Daily Report Pipeline Starting ====="
log "Project: $PROJECT_DIR"
log "Timezone: $(date +%Z)"

# Ensure we're in the backend directory for uv
cd "$PROJECT_DIR/backend"

# Run the pipeline
log "Running daily-scheduler pipeline..."
if uv run daily-scheduler run >> "$LOG_FILE" 2>&1; then
    log "===== Pipeline Completed Successfully ====="
else
    EXIT_CODE=$?
    log "===== Pipeline Failed (exit code: $EXIT_CODE) ====="
    exit $EXIT_CODE
fi
