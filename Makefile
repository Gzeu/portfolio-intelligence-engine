.PHONY: install test lint validation

install:
	python -m pip install -e .[dev]
	python -m pip install pytest pytest-asyncio

test:
	pytest -q

lint:
	python -m ruff check src tests

validation: test

