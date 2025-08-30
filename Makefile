.PHONY: help install test test-unit test-integration coverage lint format type-check security clean docker-up docker-down docker-clean ci dev

# Default target
help:
	@echo "Task Management API - Available Commands:"
	@echo ""
	@echo "Development Setup:"
	@echo "  install         Install all dependencies"
	@echo "  dev             Setup development environment"
	@echo ""
	@echo "Testing:"
	@echo "  test            Run full test suite (unit + integration) with Docker database"
	@echo "  test-unit       Run unit tests only (fast)"
	@echo "  test-integration Run integration tests with database"
	@echo "  coverage        Generate HTML coverage reports"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint            Run linting checks"
	@echo "  format          Auto-format code (black + isort)"
	@echo "  format-check    Check formatting without changes"
	@echo "  type-check      Run mypy type checking"
	@echo "  security        Run bandit security scan"
	@echo ""
	@echo "Docker Management:"
	@echo "  docker-up       Start test database"
	@echo "  docker-down     Stop test database"
	@echo "  docker-clean    Stop and remove database volumes"
	@echo ""
	@echo "Workflows:"
	@echo "  ci              Full CI pipeline (format-check + lint + type + security + test)"
	@echo "  clean           Clean up generated files"

# Development setup
install:
	@echo "Installing dependencies..."
	uv sync --dev

dev: install
	@echo "Setting up development environment..."
	uv run pre-commit install
	@echo "Development environment ready!"
	@echo "Run 'make docker-up' to start the test database"

# Docker management
docker-up:
	@echo "Starting test database..."
	docker-compose -f docker-compose.test.yml up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "Running database migrations..."
	uv run alembic upgrade head

docker-down:
	@echo "Stopping test database..."
	docker-compose -f docker-compose.test.yml down

docker-clean: docker-down
	@echo "Removing database volumes..."
	docker-compose -f docker-compose.test.yml down -v
	docker system prune -f

# Testing
test: docker-up
	@echo "Running full test suite (unit + integration tests)..."
	@echo "Running tests..."
	uv run pytest tests/ -v --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Test completed. See htmlcov/index.html for coverage report"

test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/unit/ -v --cov-report=html --cov-report=term-missing

test-integration: docker-clean docker-up
	@echo "Running integration tests..."
	uv run pytest tests/integration/ -v --disable-warnings

coverage:
	@echo "Generating coverage reports..."
	uv run pytest tests/ --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated in htmlcov/"
	@echo "Opening coverage report..."
	open htmlcov/index.html

# Code quality
lint:
	@echo "Running linting checks..."
	uv run flake8 domain/ application/ infrastructure/ presentation/ main.py

format:
	@echo "Formatting code..."
	uv run black domain/ application/ infrastructure/ presentation/ main.py tests/
	uv run isort domain/ application/ infrastructure/ presentation/ main.py tests/

format-check:
	@echo "Checking code formatting..."
	uv run black --check --diff domain/ application/ infrastructure/ presentation/ main.py tests/
	uv run isort --check-only --diff domain/ application/ infrastructure/ presentation/ main.py tests/

type-check:
	@echo "Running type checking..."
	uv run mypy domain/ application/ infrastructure/ presentation/ main.py

security:
	@echo "Running security scan..."
	uv run bandit -r domain/ application/ infrastructure/ presentation/ main.py

# Tox environments
tox-test:
	@echo "Running tox test environment..."
	uv run tox -e test

tox-lint:
	@echo "Running tox lint environment..."
	uv run tox -e lint

tox-all:
	@echo "Running all tox environments..."
	uv run tox -e all

# Full CI pipeline
ci: format-check lint type-check security test
	@echo "✅ All CI checks passed!"

# Utility commands
clean:
	@echo "Cleaning up generated files..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Development server
serve:
	@echo "Starting development server..."
	uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Database operations
migrate:
	@echo "Creating new migration..."
	@read -p "Migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

migrate-up:
	@echo "Applying database migrations..."
	uv run alembic upgrade head

migrate-down:
	@echo "Rolling back last migration..."
	uv run alembic downgrade -1

# Quick database setup
db-reset: docker-clean docker-up
	@echo "Database reset complete!"

# Pre-commit hooks
pre-commit:
	@echo "Running pre-commit hooks..."
	uv run pre-commit run --all-files

# Install pre-commit hooks
hooks:
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install

# Show project status
status:
	@echo "Project Status:"
	@echo "==============="
	@echo "Python version: $(shell python --version)"
	@echo "uv version: $(shell uv --version)"
	@echo "Docker status: $(shell docker --version)"
	@echo ""
	@echo "Database status:"
	@docker-compose -f docker-compose.test.yml ps 2>/dev/null || echo "Database not running"
	@echo ""
	@echo "Last test results:"
	@ls -la htmlcov/index.html 2>/dev/null && echo "Coverage report available" || echo "No coverage report found"

# Show configuration
config:
	@echo "Project Configuration:"
	@echo "======================"
	@echo "Python executable: $(shell which python)"
	@echo "uv executable: $(shell which uv)"
	@echo "Current directory: $(shell pwd)"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "Database URL: postgresql+asyncpg://test_user:test_password@localhost:5433/task_management_test"