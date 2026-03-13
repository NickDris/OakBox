.PHONY: help install install-backend install-frontend \
       dev dev-backend dev-frontend \
       lint lint-backend lint-frontend \
       format format-backend format-frontend \
       typecheck typecheck-backend typecheck-frontend \
       test test-backend test-frontend \
       build build-backend build-frontend \
       docker-up docker-down docker-build docker-logs docker-shell-backend \
       db-migrate db-upgrade db-downgrade \
       clean

# --------------------------------------------------------------------------- #
#  Variables
# --------------------------------------------------------------------------- #

COMPOSE := docker compose -f docker/docker-compose.yml
UV      := uv
NPM     := npm --prefix src/frontend

# --------------------------------------------------------------------------- #
#  Help
# --------------------------------------------------------------------------- #

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'

# --------------------------------------------------------------------------- #
#  Install
# --------------------------------------------------------------------------- #

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python dependencies via uv
	$(UV) sync

install-frontend: ## Install Node dependencies via npm
	$(NPM) install

# --------------------------------------------------------------------------- #
#  Development
# --------------------------------------------------------------------------- #

dev: ## Start both backend and frontend dev servers (requires two terminals or use docker)
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals,"
	@echo "or use 'make docker-up' for the full stack."

dev-backend: ## Start backend dev server
	$(UV) run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend dev server
	$(NPM) run dev

# --------------------------------------------------------------------------- #
#  Lint
# --------------------------------------------------------------------------- #

lint: lint-backend lint-frontend ## Lint all code

lint-backend: ## Lint Python code with ruff
	$(UV) run ruff check src/backend tests/backend

lint-frontend: ## Lint React/TS code with ESLint
	$(NPM) run lint

# --------------------------------------------------------------------------- #
#  Format
# --------------------------------------------------------------------------- #

format: format-backend format-frontend ## Format all code

format-backend: ## Format Python code with ruff
	$(UV) run ruff format src/backend tests/backend
	$(UV) run ruff check --fix src/backend tests/backend

format-frontend: ## Format React/TS code with Prettier
	$(NPM) run format

# --------------------------------------------------------------------------- #
#  Typecheck
# --------------------------------------------------------------------------- #

typecheck: typecheck-backend typecheck-frontend ## Typecheck all code

typecheck-backend: ## Typecheck Python with mypy
	$(UV) run mypy src/backend

typecheck-frontend: ## Typecheck React/TS with tsc
	$(NPM) run typecheck

# --------------------------------------------------------------------------- #
#  Test
# --------------------------------------------------------------------------- #

test: test-backend test-frontend ## Run all tests

test-backend: ## Run Python tests with pytest
	$(UV) run pytest tests/backend -v

test-frontend: ## Run React tests with Vitest
	$(NPM) run test -- --run

# --------------------------------------------------------------------------- #
#  Build
# --------------------------------------------------------------------------- #

build: build-backend build-frontend ## Build all artifacts

build-backend: ## Build Python package
	$(UV) build

build-frontend: ## Build frontend for production
	$(NPM) run build

# --------------------------------------------------------------------------- #
#  Docker
# --------------------------------------------------------------------------- #

docker-up: ## Start all services via Docker Compose
	$(COMPOSE) up -d

docker-down: ## Stop all services
	$(COMPOSE) down

docker-build: ## Build all Docker images
	$(COMPOSE) build

docker-logs: ## Tail logs from all services
	$(COMPOSE) logs -f

docker-shell-backend: ## Open a shell in the backend container
	$(COMPOSE) exec backend /bin/sh

# --------------------------------------------------------------------------- #
#  Database
# --------------------------------------------------------------------------- #

db-migrate: ## Create a new Alembic migration (usage: make db-migrate msg="add users table")
	$(UV) run alembic revision --autogenerate -m "$(msg)"

db-upgrade: ## Apply all pending migrations
	$(UV) run alembic upgrade head

db-downgrade: ## Revert the last migration
	$(UV) run alembic downgrade -1

# --------------------------------------------------------------------------- #
#  Clean
# --------------------------------------------------------------------------- #

clean: ## Remove build artifacts, caches, and temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -path "*/frontend/*" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -path "*/frontend/*" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .venv
	@echo "Cleaned."
