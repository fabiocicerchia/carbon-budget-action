# A budget in gCO2e, so `make run` has something to gate against. The action
# itself takes this from the `budget-gco2e` input.
BUDGET_GCO2E ?= 5000

# Every verb this repository exposes lives here; `make` on its own prints them.
# FC-GEN-057: the same eight verbs in every repo, each either wired or a
# declared no-op that says why. None of them exit 0 quietly.

.DEFAULT_GOAL := help

.PHONY: help setup install build run test lint format analyze

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

setup: ## Install the dev dependencies and the pre-commit hook
	pip install -r requirements-dev.txt
	pre-commit install

run: ## Run the estimator locally (BUDGET_GCO2E=... make run)
	BUDGET_GCO2E=$(BUDGET_GCO2E) python3 carbon_budget.py

test: ## Run the tests
	pytest -q

lint: ## Run the whole gate — every hook, every file
	pre-commit run --all-files

format: ## Format the tree with ruff, the formatter the gate checks
	ruff format .

analyze: ## Scan the tree the way CI does — vulnerabilities, misconfig, secrets
	@command -v trivy >/dev/null 2>&1 || { \
		echo "analyze needs trivy: https://trivy.dev/latest/getting-started/installation/" >&2; \
		exit 69; }
	trivy fs --scanners vuln,misconfig,secret --severity CRITICAL,HIGH .

# --- Declared no-ops (FC-GEN-058) ---
# These exit 0 and say why. They are listed under "Not applicable" in the README.

install: ## Not applicable — an action is referenced, not installed
	@echo "Nothing to install: consumers name this action in a workflow step."
	@echo "'make setup' installs what you need to work on it."
	@echo "See README > Not applicable."

build: ## Not applicable — nothing is compiled or packaged
	@echo "Nothing to build: action.yml is a composite action that runs"
	@echo "carbon_budget.py from the checkout. See README > Not applicable."
