# Research: YASL Presence Attribute

**Feature**: `001-yasl-presence-attribute`
**Date**: 2025-11-27

## Decisions

### 1. Implementation of `presence` attribute

**Decision**: Replace `required: bool` with `presence: Literal['required', 'preferred', 'optional']` in `Property` model.

**Rationale**:
-   `required` is boolean and cannot support "preferred" (warning).
-   `presence` is more expressive and extensible.
-   `optional` is the sensible default.

### 2. Validation Logic for `preferred`

**Decision**: Implement "preferred" checks *after* Pydantic validation in `load_and_validate_data_with_lines`.

**Rationale**:
-   Pydantic validation is strict and designed for errors.
-   "Preferred" fields should not block validation (they are technically optional in the Pydantic model).
-   Checking `model_fields_set` on the validated instance allows us to detect missing fields that were not provided in the input data.
-   We can access the `YaslRegistry` to look up the `presence` configuration for each field.

### 3. Handling Legacy `required` Attribute

**Decision**: Strict removal. The schema parser will reject schemas with `required`.

**Rationale**:
-   Avoids ambiguity and maintenance overhead of supporting two ways to define requirement.
-   Forces users to update to the new, clearer syntax.
-   Consistent with the "Constitution" principle of simplicity.

## Alternatives Considered

### Custom Pydantic Validator for Warnings
-   **Idea**: Use a `model_validator` to check for missing preferred fields and log warnings.
-   **Rejected**: Pydantic validators are primarily for data integrity and raising errors. Logging side-effects inside validators can be messy and might not integrate well with the overall reporting structure. Post-validation check is cleaner.

### `required: bool` + `preferred: bool`
-   **Idea**: Keep `required` and add `preferred`.
-   **Rejected**: Confusing. What if both are true? `presence` enum is mutually exclusive and clearer.
