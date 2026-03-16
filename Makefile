.PHONY: setup dev dev-backend dev-frontend test lint build clean

# ============================================================
# Daily Scheduler - Development Commands
# ============================================================

setup: ## Initial project setup
	cp -n .env.example .env 2>/dev/null || true
	cd backend && uv sync
	cd frontend && yarn install
	cd backend && uv run daily-scheduler init-db
	@echo "\n✅ Setup complete! Edit .env with your credentials, then run: make dev"

dev: ## Start both backend and frontend in dev mode
	@echo "Starting backend on http://localhost:8000 ..."
	@echo "Starting frontend on http://localhost:5173 ..."
	@$(MAKE) dev-backend & $(MAKE) dev-frontend

dev-backend: ## Start FastAPI dev server with auto-reload
	cd backend && uv run uvicorn daily_scheduler.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend: ## Start Vite dev server
	cd frontend && yarn dev

test: ## Run backend tests
	cd backend && uv run pytest -v

lint: ## Run linting and type checking
	cd backend && uv run ruff check src/
	cd backend && uv run ruff format --check src/
	cd backend && uv run mypy src/

format: ## Auto-format code
	cd backend && uv run ruff check --fix src/
	cd backend && uv run ruff format src/

build: ## Build frontend for production
	cd frontend && yarn build

run: ## Run the daily report pipeline manually
	cd backend && uv run daily-scheduler run

serve: ## Start production server (serves API + built frontend)
	cd backend && uv run daily-scheduler serve

check: ## Verify configuration and dependencies
	cd backend && uv run daily-scheduler check

install-scheduler: ## Install macOS launchd scheduler
	bash scheduler/install.sh

clean: ## Remove generated files
	rm -rf backend/.venv frontend/node_modules frontend/dist
	rm -rf backend/src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
