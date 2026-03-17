# CLAUDE.md - Project Rules

## Project Overview
Daily Scheduler: AI-powered daily news & trading report system with self-improving retrospective.
Open-source (Apache 2.0) monorepo with Python backend and Next.js frontend.
- **Intent Specification**: See [SPEC.md](SPEC.md) for system behaviors and acceptance criteria

## Architecture
- **Backend**: Hexagonal Architecture (Ports & Adapters) with Python + FastAPI + uv
- **Frontend**: Next.js (App Router, latest stable) + Tailwind CSS + Recharts
- **Database**: SQLite via SQLAlchemy
- **Scheduler**: macOS launchd, integrated into `make dev` (Ctrl+C stops all)
- **Package Managers**: uv (backend), Yarn Berry (frontend)
- **Constants**: Tunable defaults in `backend/src/daily_scheduler/constants.py` (not .env)

## Rules

### Testing
- **All logic MUST have corresponding test code** — every use case, adapter, and utility must be tested
- Unit tests: mock external dependencies (ports), test business logic in isolation
- Integration tests: test real external services (SMTP, yfinance, Claude CLI, DB) with `--integration` flag
- All E2E test cases MUST be verified with Playwright MCP tools before writing test code
- Use Playwright for E2E tests: navigate to the page, interact with elements, verify outcomes
- Backend unit tests use pytest with in-memory SQLite
- Frontend tests use Playwright for E2E scenarios
- Run `make test` before committing
- Run `uv run pytest tests/ --integration` to verify external service connectivity

### Code Quality & Static Analysis
- Backend: ruff (lint + format, line-length 100), pyrefly (type checking), pylint (10.00/10 required), mypy (strict)
- Frontend: ESLint (Next.js rules), oxlint (additional bug detection), TypeScript strict
- pylint errors and warnings MUST all be resolved — zero tolerance
- All static analysis runs automatically via PostToolUse hooks on file edit
- All code must be in English (comments, variable names, UI strings)
- Report/email language is controlled by REPORT_LANGUAGE env var

### Git
- No Co-Authored-By lines in commit messages
- Conventional commits (feat:, fix:, refactor:, test:, docs:, chore:)
- Secrets (.env, *.db) must NEVER be committed

### Development Methodology (SDD + TDD)
- **Schema-Driven Design**: Define schemas/types/interfaces BEFORE implementation
  - Domain entities → Ports → DTOs → API schemas → Frontend types
- **Test-Driven Development**: Write tests BEFORE code
  - Red → Green → Refactor cycle
  - Backend: pytest with in-memory SQLite
  - Frontend: Playwright E2E via MCP tools
- Run `make test` before committing — includes pytest, pyrefly, pylint, typecheck, oxlint

### Architecture Principles
- Hexagonal Architecture: domain logic has no framework dependencies
- Ports (interfaces) define boundaries; adapters implement them
- Nested directory structure (avoid flat sprawl)
- All external references and best practices must be followed

### Configuration
- **`.env`**: Only secrets and environment-specific values (SMTP credentials, API keys, paths)
- **`constants.py`**: Tunable operational defaults (timeouts, retries, expiry periods, lookback days)
- Never put non-secret tunables in `.env`; use `constants.py` instead
- `SCHEDULE_TIME` in `.env` controls the daily run time (HH:MM in KST)

### Dependencies
- Check license compatibility with Apache 2.0 before adding any dependency
- yfinance requires DISCLAIMER.md with Yahoo ToS notice
