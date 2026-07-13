.PHONY: help setup dev lint test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

setup: ## Install git hooks and pre-commit
	git config core.hooksPath .githooks
	@command -v pre-commit >/dev/null 2>&1 && pre-commit install || true

dev: ## Install dev dependencies
	pip install pytest ruff requests

lint: ## Run ruff
	ruff check .

test: ## Run tests
	pytest -q
