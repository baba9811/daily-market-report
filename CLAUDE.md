# CLAUDE.md - Project Rules

## Project Overview
Daily Scheduler: AI-powered daily news & trading report system with self-improving retrospective.
Open-source (Apache 2.0) monorepo with Python backend and Next.js frontend.

## Architecture
- **Backend**: Hexagonal Architecture (Ports & Adapters) with Python + FastAPI + uv
- **Frontend**: Next.js (App Router, latest stable) + Tailwind CSS + Recharts
- **Database**: SQLite via SQLAlchemy
- **Scheduler**: macOS launchd
- **Package Managers**: uv (backend), Yarn Berry (frontend)

## Rules

### Testing
- All E2E test cases MUST be verified with Playwright MCP tools before writing test code
- Use Playwright for E2E tests: navigate to the page, interact with elements, verify outcomes
- Backend unit tests use pytest with in-memory SQLite
- Frontend tests use Playwright for E2E scenarios
- Run `make test` before committing

### Code Quality
- Backend: ruff (lint + format, line-length 100), mypy (strict)
- Frontend: TypeScript strict mode, ESLint
- All code must be in English (comments, variable names, UI strings)
- Report/email language is controlled by REPORT_LANGUAGE env var

### Git
- No Co-Authored-By lines in commit messages
- Conventional commits (feat:, fix:, refactor:, test:, docs:, chore:)
- Secrets (.env, *.db) must NEVER be committed

### Architecture Principles
- Hexagonal Architecture: domain logic has no framework dependencies
- Ports (interfaces) define boundaries; adapters implement them
- Nested directory structure (avoid flat sprawl)
- All external references and best practices must be followed

### Dependencies
- Check license compatibility with Apache 2.0 before adding any dependency
- yfinance requires DISCLAIMER.md with Yahoo ToS notice
