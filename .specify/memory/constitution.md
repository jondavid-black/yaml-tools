
<!--
Sync Impact Report
Version change: 1.0.0 → 1.1.0
Modified principles: All (template → concrete)
Added sections: None
Removed sections: None
Templates requiring updates: plan-template.md (✅), spec-template.md (✅), tasks-template.md (✅)
Follow-up TODOs: TODO(RATIFICATION_DATE): Original ratification date unknown, needs confirmation.
-->

# YAML-TOOLS Constitution


## Core Principles

### I. Code Quality and Simplicity
All code MUST be clear, concise, and easy to maintain. Favor simplicity over complexity. Shared logic is placed in `src/common`. Avoid unnecessary abstractions. Each application resides in its own folder under `src/`.

### II. Testing Discipline
All code MUST be covered by unit tests using `pytest` and acceptance tests using `behave` (BDD). Tests for each application reside in `tests/<app>` and `features/<app>`. No code is merged without passing tests.

### III. Unified Tooling and Environment
Development and CI/CD MUST use Python 3.12+ and the `uv` tool for environment management. All quality checks, formatting, and test runs MUST use `uv run` in the terminal. `ruff` is used for linting and formatting. GitHub Actions is the only CI/CD system.

### IV. Single-Package Management
All tools are managed in a single repository and published as a unified `yaml-tools` package. Each application is defined as a script in `pyproject.toml`. The repository structure is: `src/` (code), `tests/` (unit tests), `features/` (BDD), `docs/` (documentation).

### V. Documentation and Transparency
All tools and APIs MUST be documented in the `docs/` folder using MkDocs Material. Documentation is updated with every feature or breaking change. All changes are tracked in version control.


## Additional Constraints

- Only Python 3.12+ is supported.
- All dependencies are managed via `uv` and declared in `pyproject.toml`.
- All code must pass `ruff` linting and formatting before merge.
- All tests and checks are run via `uv run`.
- CI/CD is enforced via GitHub Actions.


## Development Workflow

- All changes are proposed via pull requests.
- Every PR must pass all tests, linting, and formatting checks in CI.
- Code reviews are mandatory for all non-trivial changes.
- Documentation must be updated for all new features and changes.
- Releases are made from the main branch and published as a single package.


## Governance

- This constitution supersedes all other project practices.
- Amendments require a PR, review, and explicit approval by project maintainers.
- All amendments must include a migration plan if breaking changes are introduced.
- Constitution versioning follows semantic versioning:
	- MAJOR: Backward-incompatible changes to principles or governance.
	- MINOR: New principles or sections, or expanded guidance.
	- PATCH: Clarifications, typo fixes, or non-semantic refinements.
- Compliance is reviewed on every PR and at each release.
- For runtime guidance, refer to `README.md` and `docs/`.


**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): Original ratification date unknown, needs confirmation. | **Last Amended**: 2025-10-27
