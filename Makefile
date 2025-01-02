install:
	poetry install --with dev --no-root --no-interaction

format-check:
	poetry run ruff check --fix

