# sian-process-intelligence — tarefas comuns
# Uso: make <target>

PYTHON ?= python
VENV ?= .venv
DBT_DIR ?= dbt

.PHONY: help install lint format test dbt-run dbt-test clean

help:
	@echo "Targets: install, lint, format, test, dbt-run, dbt-test, clean"

install:
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Considere: uv sync (se usar uv)"

lint:
	ruff check src tests
	@echo "dbt: cd $(DBT_DIR) && dbt compile  # valida sintaxe"

format:
	ruff format src tests

test:
	pytest tests -v

dbt-run:
	cd $(DBT_DIR) && dbt run

dbt-test:
	cd $(DBT_DIR) && dbt test

dbt-docs:
	cd $(DBT_DIR) && dbt docs generate && dbt docs serve

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(DBT_DIR)/target $(DBT_DIR)/logs
