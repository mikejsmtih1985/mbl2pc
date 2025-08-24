.PHONY: install test test-parallel lint format type-check pre-commit clean ci

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest -xvs --cov=mbl2pc

test-parallel:
	pytest -n auto --cov=mbl2pc

lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy src

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/ .coverage htmlcov/

ci: lint type-check test
