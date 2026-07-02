.PHONY: setup run clean lint format

setup:
	uv sync

run:
	uv run --project . --quiet pyshell

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	uv cache clean
