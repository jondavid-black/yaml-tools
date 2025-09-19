# YAML Tools

YAML tools is a suite of advanced tools that streamline data management of structured data in YAML.

These tools include:
 - [YASL](./src/yasl/README.md) - YAML Advanced Scheme Language
 - [YAQL](./src/yaql/README.md) - YAML Advanced Query Language
 - [YARL](./src/yarl/README.md) - YAML Advanced Reporting Language

## Developer Setup

YAML tools is written in python and managed with the `UV` tool.

Setup:
- `curl -LsSf https://astral.sh/uv/install.sh | sh` to install `UV`.
- `uv venv` to create a virtual environment.
- `source .venv/bin/activate` to activate the virtual environment.
- `uv pip install -e .[dev]` to install all dependencies.

Run Unit Tests:  `uv run pytest`

Run Unit Tests w/ Coverage:  `uv run pytest --cov=src --cov-fail-under=75` 

Run Formatter:  `uv run ruff check src/ tests/`

Use the standard github-flow working process to best leverage feedback from the CI process.

To Perform a release:
- Complete and merge the pull release to main.
- Get on the main branch:
    - `git checkout main`
    - `git pull origin main`
- Tag and push the repo the repo:
    - `git tag "v$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")"`
    - `git push --tags`