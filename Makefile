.DEFAULT_GOAL := help
PY ?= python3.12
VENV := .venv
BIN := $(VENV)/bin
TF_DIR := infra/live

.PHONY: help setup lint fmt test data tf-fmt tf-validate tf-plan clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

setup: ## Create virtualenv, install package + dev tools, install git hooks
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"
	$(BIN)/pre-commit install

lint: ## Lint Python and check Terraform formatting
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .
	terraform fmt -check -recursive infra

fmt: ## Auto-format Python and Terraform
	$(BIN)/ruff format .
	$(BIN)/ruff check --fix .
	terraform fmt -recursive infra

test: ## Run unit tests
	$(BIN)/pytest

data: ## Regenerate the sample dataset (deterministic)
	cd data && ../$(BIN)/python generate_sample_orders.py

tf-validate: ## Validate the live Terraform root module (no backend)
	terraform -chdir=$(TF_DIR) init -backend=false && terraform -chdir=$(TF_DIR) validate

tf-plan: ## Plan against the remote backend (requires AWS credentials)
	terraform -chdir=$(TF_DIR) init && terraform -chdir=$(TF_DIR) plan

clean: ## Remove local build and cache files
	rm -rf build dist .pytest_cache .ruff_cache **/__pycache__
