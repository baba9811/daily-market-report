# SPEC.md - Intent Specification

> This document describes **WHAT** the system does — verifiable behaviors and acceptance criteria.
> For **HOW** to build it (architecture, conventions, tooling), see [CLAUDE.md](CLAUDE.md).
> Each spec item has a unique ID (`SECTION-NN`) that can be referenced from test names.

## System Purpose

AI-powered daily trading report system for Korean (KOSPI/KOSDAQ) and US (NYSE/NASDAQ) markets.
Runs autonomously via scheduler, generates news-driven analysis and recommendations using Claude AI,
tracks recommendation outcomes over time, and feeds performance data back into future reports
as a self-improving retrospective loop. Delivers reports via email and provides a web dashboard.

## Spec ID Convention

- Format: `SECTION-NN` (e.g., `PIPE-01`, `REC-03`)
- Tests should reference spec IDs in names where practical: `test_pipe_01_idempotent_skip`
- Multiple tests can cover one spec ID (different scenarios)

---

## Daily Pipeline (PIPE-*)

- [ ] `PIPE-01`: If a daily report already exists for today, the pipeline skips and returns success (idempotency)
- [ ] `PIPE-02`: Pipeline executes 9 sequential steps: check recommendations → update prices → build retrospective → fetch market data → screen stocks → generate report (Claude CLI) → parse response → save to DB + filesystem → send email
- [ ] `PIPE-03`: Report generation sends Claude CLI: retrospective context, weekly lessons (Mondays only), real-time market data, stock screening data
- [ ] `PIPE-04`: Response parsing tries JSON first; falls back to legacy HTML extraction if JSON parse fails
- [ ] `PIPE-05`: Empty Claude response causes pipeline failure and triggers error email
- [ ] `PIPE-06`: Unexpected exceptions are caught, logged, error email sent, pipeline returns false
- [ ] `PIPE-07`: Email failure does NOT cause pipeline failure — report is still saved
- [ ] `PIPE-08`: Reports are saved to both DB (SQLite) and filesystem (`data/reports/YYYY-MM-DD_daily.html`)
- [ ] `PIPE-09`: Monday reports include weekly analysis lessons in the prompt context
- [ ] `PIPE-10`: Stock screening covers defined universe (~63 KR + ~38 US stocks) with fundamental and technical data

## Recommendation Lifecycle (REC-*)

- [ ] `REC-01`: New recommendations start with status `OPEN`
- [ ] `REC-02`: DAY trades expire after `DAY_TRADE_EXPIRY_DAYS` (default 1 day); same-day trades are NOT expired
- [ ] `REC-03`: SWING trades expire after `SWING_TRADE_EXPIRY_DAYS` (default 14 days)
- [ ] `REC-04`: LONG target hit when `current_price >= target_price` → status `TARGET_HIT`
- [ ] `REC-05`: LONG stop hit when `current_price <= stop_loss` → status `STOP_HIT`
- [ ] `REC-06`: SHORT target hit when `current_price <= target_price` → status `TARGET_HIT`
- [ ] `REC-07`: SHORT stop hit when `current_price >= stop_loss` → status `STOP_HIT`
- [ ] `REC-08`: On target/stop hit: status changes, `closed_at` set, `closed_price` recorded, `pnl_percent` calculated
- [ ] `REC-09`: PnL LONG = `(closed_price - entry_price) / entry_price * 100`; PnL SHORT = `(entry_price - closed_price) / entry_price * 100`
- [ ] `REC-10`: If price fetch fails (returns None), recommendation is left unchanged
- [ ] `REC-11`: Expiry check runs BEFORE price check — expired trades skip price checking
- [ ] `REC-12`: Each recommendation has: ticker, name, market, direction (LONG/SHORT), timeframe (DAY/SWING), entry/target/stop prices, rationale, sector

## Report Content (RPT-*)

- [ ] `RPT-01`: Report contains: market_summary, alert_banner, news_items, causal_chains, risk_matrix, sector_analysis, sentiment, technicals, recommendations, upcoming_events, past_performance_commentary, disclaimer
- [ ] `RPT-02`: News items have: category, headline, source, published_at, summary, impact_level, affected_sectors
- [ ] `RPT-03`: Recommendations include: risk_reward_ratio (>= 1.5), confidence level, causal_chain_summary
- [ ] `RPT-04`: HTML reports are rendered from Jinja2 template when JSON parsing succeeds
- [ ] `RPT-05`: Report language is controlled by `REPORT_LANGUAGE` env var (default: Korean)

## Retrospective (RETRO-*)

- [ ] `RETRO-01`: Daily retrospective looks back `RETROSPECTIVE_LOOKBACK_DAYS` (default 30 days)
- [ ] `RETRO-02`: Context includes: summary statistics, sector performance, strategy performance (DAY vs SWING), recent 7-day table, auto-derived lessons
- [ ] `RETRO-03`: Auto-derived lessons flag sectors with win rate below 30% as warnings, above 70% as opportunities
- [ ] `RETRO-04`: Auto-derived lessons compare DAY vs SWING win rates if difference exceeds 10 percentage points
- [ ] `RETRO-05`: Weekly analysis (Mondays only) computes: wins, losses, avg return, best/worst picks, sector breakdown
- [ ] `RETRO-06`: If no past data exists, context says "No past recommendation data available"

## API Contracts (API-*)

- [ ] `API-01`: `GET /api/dashboard` → latest report info, open rec count, 7-day win rate, 7-day closed count, today's alerts
- [ ] `API-02`: `GET /api/reports` → paginated list (`page`, `per_page`), filterable by `report_type`, sorted newest first
- [ ] `API-03`: `GET /api/reports/latest` → most recent daily report with HTML; 404 if none exist
- [ ] `API-04`: `GET /api/reports/{id}` → specific report; 404 if not found
- [ ] `API-05`: `GET /api/reports/{id}/html` → raw HTML with `text/html` content type
- [ ] `API-06`: `GET /api/performance/summary?period=30d` → total, open, target_hit, stop_hit, expired, win_rate, avg_pnl, best/worst picks
- [ ] `API-07`: `GET /api/performance/recommendations` → filterable by `status` (all/OPEN/TARGET_HIT/STOP_HIT/EXPIRED)
- [ ] `API-08`: `GET /api/performance/sectors?period=30d` → per-sector wins, losses, win_rate, avg_return
- [ ] `API-09`: `GET /api/performance/timeseries?period=30d` → daily data points with cumulative PnL and win rate
- [ ] `API-10`: `GET /api/retrospective/weekly` → paginated weekly analyses
- [ ] `API-11`: `GET /api/retrospective/daily-checks?limit=14` → recent daily check results
- [ ] `API-12`: `POST /api/pipeline/run` → triggers pipeline in background; returns `already_running` if in progress; prevents concurrent runs
- [ ] `API-13`: `GET /api/pipeline/status` → running state and last result
- [ ] `API-14`: `GET /api/settings` → current config with passwords masked as boolean
- [ ] `API-15`: `PUT /api/settings` → updates only safe fields (SMTP, email, claude_model, report_language); blocks claude_cli_path, database_url
- [ ] `API-16`: `POST /api/settings/test-email` → sends test email, returns success/failure
- [ ] `API-17`: `GET /api/settings/status` → health check: DB exists, Claude CLI reachable, SMTP configured

## Frontend Pages (UI-*)

- [ ] `UI-01`: Dashboard (`/`) shows: 4 stat cards (open recs, weekly closed, 7-day win rate, latest report date), win rate gauge, today's alerts list
- [ ] `UI-02`: Dashboard gracefully degrades — shows zeros/empty state when API is unavailable
- [ ] `UI-03`: Reports page (`/reports`) shows paginated list with date, type, summary (truncated 200 chars), generation time
- [ ] `UI-04`: Report detail (`/reports/[id]`) renders full HTML content of the report
- [ ] `UI-05`: Performance page (`/performance`) shows: PnL/win rate timeseries chart, sector breakdown bars, recommendations table
- [ ] `UI-06`: Retrospective page (`/retrospective`) shows: daily checks table, weekly analyses with sector breakdown
- [ ] `UI-07`: Settings page (`/settings`) shows: config form (safe fields only), system status indicators (DB, CLI, SMTP)

## Configuration Effects (CFG-*)

- [ ] `CFG-01`: `SCHEDULE_TIME` (env, HH:MM KST) controls daily pipeline run time
- [ ] `CFG-02`: `REPORT_LANGUAGE` (env) controls generated report language (ko/en/ja)
- [ ] `CFG-03`: `DAY_TRADE_EXPIRY_DAYS` (constants.py, default 1) controls DAY trade expiry window
- [ ] `CFG-04`: `SWING_TRADE_EXPIRY_DAYS` (constants.py, default 14) controls SWING trade expiry window
- [ ] `CFG-05`: `RETROSPECTIVE_LOOKBACK_DAYS` (constants.py, default 30) controls retrospective analysis range
- [ ] `CFG-06`: `RECENT_PERIOD_DAYS` (constants.py, default 7) controls "recent" window in retrospective table
- [ ] `CFG-07`: `CLAUDE_TIMEOUT_SECONDS` (constants.py, default 1200) controls max wait for Claude CLI
- [ ] `CFG-08`: `CLAUDE_RETRY_COUNT` / `CLAUDE_RETRY_DELAY_SECONDS` (constants.py) control Claude CLI retry behavior
- [ ] `CFG-09`: `EMAIL_MAX_RETRIES` / `EMAIL_BACKOFF_BASE` (constants.py) control email retry with exponential backoff
- [ ] `CFG-10`: `SUMMARY_MAX_LENGTH` (constants.py, default 200) controls report summary truncation

## Error Handling (ERR-*)

- [ ] `ERR-01`: Pipeline catches all exceptions, logs them, sends error email, returns false
- [ ] `ERR-02`: Email failure is non-fatal — reports are saved regardless
- [ ] `ERR-03`: Price fetch failure for one recommendation does not affect others
- [ ] `ERR-04`: Pipeline trigger endpoint prevents concurrent runs via thread lock
- [ ] `ERR-05`: Claude CLI calls have configurable timeout and retry with delay

## Data Integrity (DATA-*)

- [ ] `DATA-01`: Only one daily report per date (enforced by idempotency check)
- [ ] `DATA-02`: Reports persisted to both DB (queryable) and filesystem (portable HTML)
- [ ] `DATA-03`: Settings API blocks writes to security-sensitive fields (claude_cli_path, database_url)
- [ ] `DATA-04`: Secrets never exposed in API responses — password shown only as boolean `smtp_password_set`

---

## Test Traceability

- Backend tests should include spec IDs in function names: `test_rec_02_day_trade_expires`
- Frontend E2E tests (Playwright) should follow same convention: `test_ui_01_dashboard_stat_cards`
- No mapping table maintained here — grep spec IDs across test files to find coverage
