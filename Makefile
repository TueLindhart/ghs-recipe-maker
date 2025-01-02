install:
	poetry install --with dev --no-root --no-interaction

lint:
	poetry run ruff check --fix

format:
	poetry run ruff format

type-check:
	poetry run pyright

all: install lint-check format

