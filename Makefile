.PHONY: help install dev lint test proto clean docker

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install UEWM
	pip install -e .

dev: ## Install in development mode
	pip install -e ".[dev]"
	pre-commit install

lint: ## Run linters
	ruff check src/
	black --check src/
	mypy src/ --ignore-missing-imports
	buf lint proto/

format: ## Auto-format code
	black src/ tests/
	ruff check --fix src/

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests
	pytest tests/integration/ -v

proto: ## Compile Protobuf IDL
	buf generate proto/

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

docker-build: ## Build Docker images
	docker build -t uewm/brain-core -f docker/Dockerfile.brain .
	docker build -t uewm/eip-gateway -f docker/Dockerfile.gateway .

docker-up: ## Start local dev environment
	docker compose up -d

docker-down: ## Stop local dev environment
	docker compose down
