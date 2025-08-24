.PHONY: install test test-parallel lint format type-check pre-commit clean ci run dev docker-build docker-run requirements help

# Default target
help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install development dependencies and setup pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install

run:  ## Run the development server with auto-reload
	uvicorn src.mbl2pc.main:app --reload --host 0.0.0.0 --port 8000

dev: install run  ## Setup and run development environment

test:  ## Run all tests with coverage
	pytest -xvs --cov=src/mbl2pc --cov-report=html --cov-report=term

test-parallel:  ## Run tests in parallel (faster)
	pytest -n auto --cov=src/mbl2pc --cov-report=html

test-unit:  ## Run only unit tests
	pytest tests/unit/ -v

test-integration:  ## Run only integration tests
	pytest tests/integration/ -v

test-e2e:  ## Run only end-to-end tests
	pytest tests/e2e/ -v

lint:  ## Run Ruff linting
	ruff check .

format:  ## Run Ruff formatting
	ruff format .

type-check:  ## Run MyPy type checking
	mypy src

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

requirements:  ## Generate requirements.txt from pyproject.toml
	pip-compile --output-file=requirements.txt pyproject.toml

docker-build:  ## Build Docker image
	docker build -t mbl2pc .

docker-run:  ## Run application in Docker
	docker-compose up

docker-dev:  ## Run with LocalStack for local AWS services
	docker-compose --profile localdev up

clean:  ## Clean up generated files
	rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ci: lint type-check test  ## Run all CI checks (linting, type checking, tests)
