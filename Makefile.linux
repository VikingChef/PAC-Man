CONFIG ?= config.json
export PYGAME_HIDE_SUPPORT_PROMPT := 1
export PYTHONPATH := src

install:
	uv sync

run:
	PYTHONPATH=src uv run python pac-man.py config.json

debug:
	uv run python -m pdb pac-man.py $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
