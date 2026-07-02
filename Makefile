.PHONY: setup run clean

setup:
	uv sync

run:
	uv run --project . --quiet -m app.main $(ARGS)

clean:
	uv cache clean
