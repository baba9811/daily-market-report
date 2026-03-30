#!/bin/bash
set -euo pipefail

# ============================================================
# Daily Scheduler - Run Korean News Briefing Pipeline
# Triggered by macOS launchd, Linux cron, or manually
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/scheduler.log"

# Load user PATH (cron runs with minimal PATH)
if [ -f "$HOME/.profile" ]; then
    . "$HOME/.profile"
fi
if [ -f "$HOME/.bashrc" ]; then
    . "$HOME/.bashrc"
fi
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [NEWS] $1" | tee -a "$LOG_FILE"
}

log "===== Korean News Briefing Pipeline Starting ====="
log "Project: $PROJECT_DIR"
log "Timezone: $(date +%Z)"

# Ensure we're in the backend directory for uv
cd "$PROJECT_DIR/backend"

# Run the pipeline
log "Running news briefing pipeline..."
if uv run daily-scheduler run-news >> "$LOG_FILE" 2>&1; then
    log "===== News Briefing Pipeline Completed Successfully ====="
else
    EXIT_CODE=$?
    log "===== News Briefing Pipeline Failed (exit code: $EXIT_CODE) ====="
    exit $EXIT_CODE
fi
