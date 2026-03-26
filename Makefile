.PHONY: install install-dev test lint format run run-api clean help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test: ## Run tests
	pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

lint: ## Run linter
	ruff check src/ tests/ config/

format: ## Auto-format code
	ruff format src/ tests/ config/
	ruff check --fix src/ tests/ config/

run: ## Run the Streamlit app
	streamlit run app.py

run-api: ## Run the FastAPI server
	uvicorn src.api.fastapi_app:app --reload --host 0.0.0.0 --port 8000

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ruff_cache htmlcov .coverage coverage.xml
