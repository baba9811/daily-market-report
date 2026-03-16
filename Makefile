.PHONY: all setup dev dev-backend dev-frontend test lint format build run serve check install-scheduler clean help

# ============================================================
# Daily Scheduler - Development Commands
# ============================================================
# `make` (no args) starts everything: backend + frontend + scheduler

all: dev ## Default: start backend + frontend dev servers

setup: ## Initial project setup (run once)
	cp -n .env.example .env 2>/dev/null || true
	cd backend && uv sync --extra dev
	cd frontend && yarn install
	cd backend && uv run daily-scheduler init-db
	@echo ""
	@echo "Setup complete! Edit .env with your credentials, then run: make"

dev: ## Start backend + frontend dev servers
	@echo "Starting backend on http://localhost:8000"
	@echo "Starting frontend on http://localhost:3000"
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Start FastAPI dev server (auto-reload)
	cd backend && uv run uvicorn daily_scheduler.main:app \
		--reload --host 127.0.0.1 --port 8000

dev-frontend: ## Start Next.js dev server
	cd frontend && yarn dev

test: ## Run all tests (backend unit + frontend typecheck + static analysis)
	cd backend && uv run pytest tests/ -v
	cd backend && uv run pyrefly check src/
	cd frontend && yarn typecheck
	cd frontend && yarn oxlint

lint: ## Run linting and static analysis
	cd backend && uv run ruff check src/
	cd backend && uv run ruff format --check src/
	cd backend && uv run pyrefly check src/
	cd frontend && yarn lint
	cd frontend && yarn oxlint

format: ## Auto-format all code
	cd backend && uv run ruff check --fix src/
	cd backend && uv run ruff format src/

build: ## Build frontend for production
	cd frontend && yarn build

run: ## Run the daily report pipeline once (manual trigger)
	cd backend && uv run daily-scheduler run

serve: ## Start production server (API + built frontend)
	cd backend && uv run daily-scheduler serve

check: ## Verify configuration and dependencies
	cd backend && uv run daily-scheduler check

install-scheduler: ## Install macOS launchd scheduler
	bash scheduler/install.sh

clean: ## Remove all generated files
	rm -rf backend/.venv frontend/node_modules frontend/.next
	rm -rf backend/src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all
