.PHONY: help build up down logs ps test test-unit test-integration clean restart health db-migrate db-rollback db-status shell-orchestrator shell-postgres lint format type-check pre-commit install-hooks

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)AI Transactional Agent - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker - Basic Operations

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker compose build

build-no-cache: ## Build all Docker images without cache
	@echo "$(BLUE)Building Docker images (no cache)...$(NC)"
	docker compose build --no-cache

up: ## Start all services in background
	@echo "$(GREEN)Starting services...$(NC)"
	docker compose up -d

up-build: ## Build and start all services
	@echo "$(GREEN)Building and starting services...$(NC)"
	docker compose up -d --build

down: ## Stop and remove containers
	@echo "$(RED)Stopping services...$(NC)"
	docker compose down

down-v: ## Stop and remove containers, networks, and volumes
	@echo "$(RED)Stopping services and removing volumes...$(NC)"
	docker compose down -v

restart: down up ## Restart all services

logs: ## View logs from all services
	docker compose logs -f

logs-orchestrator: ## View logs from orchestrator only
	docker compose logs -f orchestrator

logs-mock-api: ## View logs from mock-api only
	docker compose logs -f mock-api

logs-postgres: ## View logs from postgres only
	docker compose logs -f postgres

ps: ## Show status of all services
	docker compose ps

##@ Testing

test: ## Run all tests with coverage in Docker
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.test.yml build orchestrator-test
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test

test-unit: ## Run only unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
		.venv/bin/pytest tests/unit/ -v

test-integration: ## Run only integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
		.venv/bin/pytest tests/integration/ -v

test-cov: ## Run tests with detailed coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
		.venv/bin/pytest --cov=apps --cov-report=term-missing --cov-report=html --cov-report=xml -v

test-specific: ## Run specific test file (usage: make test-specific TEST=tests/unit/test_file.py)
	@echo "$(BLUE)Running specific test: $(TEST)$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test \
		.venv/bin/pytest $(TEST) -v

test-local: ## Run tests locally (requires local venv)
	@echo "$(BLUE)Running tests locally...$(NC)"
	uv run pytest -v --cov=apps --cov-report=term-missing

##@ Database

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	docker compose exec orchestrator .venv/bin/alembic upgrade head

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	docker compose exec orchestrator .venv/bin/alembic downgrade -1

db-status: ## Show current migration status
	@echo "$(BLUE)Current migration status:$(NC)"
	docker compose exec orchestrator .venv/bin/alembic current

db-history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	docker compose exec orchestrator .venv/bin/alembic history

db-shell: ## Open PostgreSQL shell
	@echo "$(BLUE)Opening PostgreSQL shell...$(NC)"
	docker compose exec postgres psql -U postgres -d transactional_agent

db-tables: ## List all database tables
	@echo "$(BLUE)Database tables:$(NC)"
	docker compose exec postgres psql -U postgres -d transactional_agent -c "\dt"

db-conversations: ## View conversations in database
	@echo "$(BLUE)Conversations:$(NC)"
	docker compose exec postgres psql -U postgres -d transactional_agent -c "SELECT id, user_id, status, created_at FROM conversations LIMIT 10;"

db-messages: ## View messages in database
	@echo "$(BLUE)Messages:$(NC)"
	docker compose exec postgres psql -U postgres -d transactional_agent -c "SELECT conversation_id, role, LEFT(content, 50) as content, timestamp FROM messages ORDER BY timestamp DESC LIMIT 10;"

db-backup: ## Backup database to file
	@echo "$(BLUE)Backing up database...$(NC)"
	docker compose exec postgres pg_dump -U postgres transactional_agent > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup created!$(NC)"

##@ Development & Debugging

shell-orchestrator: ## Open bash shell in orchestrator container
	@echo "$(BLUE)Opening shell in orchestrator...$(NC)"
	docker compose exec orchestrator /bin/bash

shell-postgres: ## Open bash shell in postgres container
	@echo "$(BLUE)Opening shell in postgres...$(NC)"
	docker compose exec postgres /bin/bash

shell-mock-api: ## Open bash shell in mock-api container
	@echo "$(BLUE)Opening shell in mock-api...$(NC)"
	docker compose exec mock-api /bin/bash

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo "$(YELLOW)Mock API:$(NC)"
	@curl -s http://localhost:8001/health | jq . || echo "$(RED)Mock API not responding$(NC)"
	@echo ""
	@echo "$(YELLOW)Orchestrator:$(NC)"
	@curl -s http://localhost:8002/health | jq . || echo "$(RED)Orchestrator not responding$(NC)"

##@ Code Quality

lint: ## Run ruff linter
	@echo "$(BLUE)Running ruff linter...$(NC)"
	uv run ruff check apps/

lint-fix: ## Run ruff linter with auto-fix
	@echo "$(BLUE)Running ruff linter with auto-fix...$(NC)"
	uv run ruff check --fix apps/

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format apps/

type-check: ## Run mypy type checking
	@echo "$(BLUE)Running type checks...$(NC)"
	uv run mypy apps/

pre-commit: ## Run all pre-commit hooks
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	uv run pre-commit run --all-files

install-hooks: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	uv run pre-commit install

##@ Cleanup

clean: ## Remove all containers, volumes, images and temp files
	@echo "$(RED)Cleaning up...$(NC)"
	docker compose down -v --rmi all --remove-orphans
	rm -rf htmlcov/ .coverage coverage.xml .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-test: ## Remove test artifacts
	@echo "$(YELLOW)Removing test artifacts...$(NC)"
	rm -rf htmlcov/ .coverage coverage.xml .pytest_cache/
	@echo "$(GREEN)Test artifacts removed!$(NC)"

##@ Quick Start

dev: down-v up-build logs ## Full dev reset: clean, build, start, and show logs

quick-start: up health ## Quick start: just start services and check health

demo: up ## Start services and run a demo transaction
	@echo "$(GREEN)Services started. Running demo transaction...$(NC)"
	@sleep 5
	@curl -X POST http://localhost:8002/api/v1/chat \
		-H "Content-Type: application/json" \
		-d '{"user_id": "demo-user", "message": "Quiero enviar 50000 pesos al 3001234567"}' | jq .

##@ Documentation

docs-serve: ## Serve API documentation
	@echo "$(BLUE)API documentation available at:$(NC)"
	@echo "$(GREEN)http://localhost:8002/docs$(NC) (Swagger UI)"
	@echo "$(GREEN)http://localhost:8002/redoc$(NC) (ReDoc)"

status: ps health ## Show status and health of all services
