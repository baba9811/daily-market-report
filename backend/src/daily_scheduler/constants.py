"""Application constants — tunable values that don't belong in .env.

These are operational defaults that rarely change between environments.
Edit this file to adjust behavior without touching .env or Settings.
"""

# ── Claude CLI ───────────────────────────────────────────────
CLAUDE_TIMEOUT_SECONDS = 600  # Max wait for a single Claude CLI call
CLAUDE_RETRY_COUNT = 2  # Number of attempts (1 = no retry)
CLAUDE_RETRY_DELAY_SECONDS = 30  # Wait between retries

# ── Email ────────────────────────────────────────────────────
EMAIL_MAX_RETRIES = 3  # SMTP send attempts
EMAIL_BACKOFF_BASE = 5  # Exponential backoff base (seconds)
EMAIL_SMTP_TIMEOUT = 30  # SMTP connection timeout (seconds)

# ── Recommendation Expiry ────────────────────────────────────
DAY_TRADE_EXPIRY_DAYS = 1  # DAY trades expire after this many days
SWING_TRADE_EXPIRY_DAYS = 14  # SWING trades expire after this many days

# ── Retrospective Analysis ───────────────────────────────────
RETROSPECTIVE_LOOKBACK_DAYS = 30  # How far back to analyze recommendations
RECENT_PERIOD_DAYS = 7  # "Recent" window for detailed table

# ── Report Parsing ───────────────────────────────────────────
SUMMARY_MAX_LENGTH = 200  # Truncation length for report summary
