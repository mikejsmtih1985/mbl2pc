.PHONY: install test test-parallel lint format type-check pre-commit clean ci

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	PYTHONPATH=src pytest -xvs --cov=src/mbl2pc

test-parallel:
	PYTHONPATH=src pytest -n auto --cov=src/mbl2pc

lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy src/mbl2pc --no-namespace-packages

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/ .coverage htmlcov/

ci: lint type-check test
