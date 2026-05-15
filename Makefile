.PHONY: install test lint clean demo docker-build docker-up docker-shell docker-test docker-down

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

docker-build:
	docker compose build

docker-up:
	docker compose up

docker-shell:
	docker compose run --rm backend sh

docker-test:
	docker compose run --rm backend pytest -q
	docker compose run --rm backend ruff check .
	docker compose run --rm backend biostack --help
	docker compose run --rm backend biostack doctor

docker-down:
	docker compose down
