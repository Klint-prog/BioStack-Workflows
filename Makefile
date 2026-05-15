.PHONY: install test lint clean demo

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .

clean:
	rm -rf demo _verify05 .pytest_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

demo:
	rm -rf demo
	biostack init demo --template rnaseq-basic
	cd demo && biostack run --dry-run && biostack report --run latest
