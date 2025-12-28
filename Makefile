.PHONY: help install test lint format clean deploy

help:
	@echo "Available commands:"
	@echo "  install       Install dependencies"
	@echo "  test          Run tests"
	@echo "  lint          Run linting"
	@echo "  format        Format code"
	@echo "  deploy        Deploy infrastructure"

install:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	pytest

lint:
	flake8 src tests --max-line-length=100
	mypy src --ignore-missing-imports

format:
	black src tests

clean:
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov **/__pycache__

deploy:
	python scripts/deploy.py
