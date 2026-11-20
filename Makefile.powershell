# PowerShell-friendly Makefile. Usage: make -f Makefile.powershell <target>
CONFIG ?= config.json
export PYGAME_HIDE_SUPPORT_PROMPT := 1
export PYTHONPATH := src

SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command

.PHONY: install run debug clean lint

install:
	uv sync

run:
	uv run python pac-man.py $(CONFIG)

debug:
	uv run python -m pdb pac-man.py $(CONFIG)

clean:
	Get-ChildItem -Path . -Recurse -Directory -Force -Include __pycache__,.mypy_cache,.pytest_cache | Remove-Item -Recurse -Force

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
