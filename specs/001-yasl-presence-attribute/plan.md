# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature replaces the boolean `required` attribute in YASL schema definitions with a new `presence` attribute. `presence` supports three values: `required` (error on missing), `preferred` (warning on missing), and `optional` (no action). This allows for more flexible schema definitions and "soft" requirements. The implementation involves updating the `Property` Pydantic model, modifying the schema parser to enforce the new attribute and reject the old one, and updating the validation logic to generate warnings for missing `preferred` fields.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `pydantic`, `ruamel.yaml`
**Storage**: Files (YAML)
**Testing**: `pytest`, `behave`
**Target Platform**: Linux/Cross-platform
**Project Type**: Library / CLI Tool
**Performance Goals**: N/A (Standard validation speed)
**Constraints**: Backward compatibility for data files (not schema files), strict schema validation.
**Scale/Scope**: Core validation logic update.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Code Quality**: Simple implementation, extending existing patterns.
- [x] **II. Testing**: Will include unit tests and BDD features.
- [x] **III. Tooling**: Uses `uv`, `ruff`.
- [x] **IV. Single-Package**: Part of `yaml-tools`.
- [x] **V. Documentation**: Docs will be updated.

## Project Structure

### Documentation (this feature)

```text
specs/001-yasl-presence-attribute/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── yasl/
│   ├── core.py          # Validation logic updates
│   ├── pydantic_types.py # Property model updates
│   └── validators.py    # (Potentially unused for this, but part of structure)
tests/
├── yasl/                # Unit tests
features/
├── yasl/                # BDD tests
```

**Structure Decision**: Option 1: Single project (Library structure)

## Complexity Tracking


> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
