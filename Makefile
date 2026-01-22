.PHONY: help install test run clean lint

help:
	@echo "School Closings Tracker - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run unit tests"
	@echo "  make run        - Run the scraper"
	@echo "  make clean      - Remove generated files"
	@echo "  make lint       - Run code quality checks"

install:
	pip install -r requirements.txt

test:
	python3 -m pytest tests/ -v

run:
	python3 school_closings_scraper.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage

lint:
	@echo "Running Python syntax check..."
	python3 -m py_compile school_closings_scraper.py
	python3 -m py_compile analyze_data.py
	python3 -m py_compile test_scraper.py
	@echo "✓ All files have valid Python syntax"
