# Viaduct Echo Backend Makefile

.PHONY: help install install-dev test lint format check clean run docker-build docker-up docker-down

# Colors for terminal output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

# Default target
help: ## Show this help message
	@echo "$(BLUE)Viaduct Echo Backend Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Installation and setup
install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	uv sync --no-dev

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	uv sync --dev
	uv run pre-commit install

# Code quality and testing
test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	uv run python -m pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting checks (Ruff + Bandit)
	@echo "$(BLUE)Running linting checks (Ruff + Bandit)...$(NC)"
	uv run ruff check src/ tests/
	uv run bandit -r src/ -f json

format: ## Format code with Black and fix import order via Ruff
	@echo "$(BLUE)Formatting code (Black + Ruff imports)...$(NC)"
	uv run black src/ tests/
	uv run ruff check --select I --fix src/ tests/

check: ## Run all checks (format check + Ruff + tests)
	@echo "$(BLUE)Running all quality checks...$(NC)"
	uv run black --check src/ tests/
	uv run ruff check src/ tests/
	uv run python -m pytest tests/ -q

# Pre-commit hooks
pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	uv run pre-commit run --all-files

# Application commands
run: ## Run the main application
	@echo "$(BLUE)Starting Viaduct Echo backend...$(NC)"
	uv run python -m src.main

run-api: ## Run the FastAPI development server
	@echo "$(BLUE)Starting FastAPI development server...$(NC)"
	uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

run-api-prod: ## Run the FastAPI production server
	@echo "$(BLUE)Starting FastAPI production server...$(NC)"
	nohup uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Database utilities
db-status: ## Check AI summary status in database
	@echo "$(BLUE)Checking AI summary status...$(NC)"
	uv run python src/database/check_ai_summary_status.py

db-backfill: ## Backfill AI summaries for articles
	@echo "$(BLUE)Starting AI summary backfill...$(NC)"
	uv run python src/database/backfill_ai_summaries.py

# Docker commands
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t viaductecho-backend .

docker-up: ## Start Docker Compose services
	@echo "$(BLUE)Starting Docker services...$(NC)"
	docker-compose up -d

docker-down: ## Stop Docker Compose services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	docker-compose down

docker-dev: ## Start Docker Compose in development mode
	@echo "$(BLUE)Starting Docker services in development mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

docker-logs: ## View Docker logs
	@echo "$(BLUE)Viewing Docker logs...$(NC)"
	docker-compose logs -f

# Cleanup commands
clean: ## Clean up generated files and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .coverage htmlcov/ build/ dist/ *.egg-info/

clean-logs: ## Clean up log files
	@echo "$(BLUE)Cleaning log files...$(NC)"
	find logs/ -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

# Development workflow shortcuts
dev-setup: install-dev ## Complete development setup
	@echo "$(GREEN)Development environment setup complete!$(NC)"

dev-check: format lint test ## Run development quality checks
	@echo "$(GREEN)All development checks passed!$(NC)"

# CI/CD related
ci: check ## Run CI pipeline (format check, lint, test)
	@echo "$(GREEN)CI pipeline completed successfully!$(NC)"

# Information commands
info: ## Show project information
	@echo "$(BLUE)Viaduct Echo Backend$(NC)"
	@echo "Python version: $(shell python --version)"
	@echo "UV version: $(shell uv --version 2>/dev/null || echo 'Not installed')"
	@echo "Docker version: $(shell docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not in git repo')"
