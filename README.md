# YAML Tools

YAML tools is a suite of advanced tools that streamline data management of structured data in YAML.

These tools include:
 - [YASL](./src/yasl/README.md) - YAML Advanced Scheme Language
 - [YAQL](./src/yaql/README.md) - YAML Advanced Query Language
 - [YARL](./src/yarl/README.md) - YAML Advanced Reporting Language

## Developer Setup

YASl is a python application built with the `UV` tool.

Setup:
- `curl -LsSf https://astral.sh/uv/install.sh | sh` to install `UV`.
- `uv venv` to create a virtual environment.
- `source .venv/bin/activate` to activate the virtual environment.
- `uv pip install -e .[dev]` to install all dependencies.

Run Unit Tests:  `uv run pytest`

Run Unit Tests w/ Coverage:  `uv run pytest --cov=src --cov-fail-under=75` 

Run Formatter:  `uv run ruff check src/ tests/`