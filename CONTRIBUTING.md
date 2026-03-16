# Contributing to Daily Scheduler

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- [Yarn Berry](https://yarnpkg.com/) (v4+)
- [Claude Code CLI](https://claude.ai/code)

### Setup

```bash
git clone https://github.com/your-username/daily-scheduler.git
cd daily-scheduler
cp .env.example .env
make setup
```

### Development

```bash
# Start both backend and frontend in dev mode
make dev

# Backend only (auto-reload)
make dev-backend

# Frontend only (Vite dev server)
make dev-frontend
```

### Testing & Linting

```bash
make test    # Run backend tests
make lint    # Run ruff + mypy
make format  # Auto-format code
```

## Project Structure

- **`backend/`** — Python backend with FastAPI
  - `src/daily_scheduler/services/` — Core business logic
  - `src/daily_scheduler/routers/` — API endpoints
  - `src/daily_scheduler/models/` — Database models
- **`frontend/`** — React SPA with Vite + Tailwind
  - `src/pages/` — Page components
  - `src/components/` — Reusable components
- **`scheduler/`** — macOS launchd configuration

## Guidelines

1. **Keep it simple** — Don't over-engineer. Simple solutions are preferred.
2. **Test your changes** — Ensure existing tests pass and add tests for new features.
3. **Follow conventions** — Use the existing code style (ruff for Python, ESLint for TypeScript).
4. **No secrets** — Never commit API keys, passwords, or personal data.
5. **Meaningful commits** — Write clear, concise commit messages.

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure tests pass (`make test && make lint`)
5. Commit your changes
6. Push to your fork
7. Open a Pull Request

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
