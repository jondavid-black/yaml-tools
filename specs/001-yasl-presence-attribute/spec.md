# Feature Specification: YASL Presence Attribute

**Feature Branch**: `001-yasl-presence-attribute`  
**Created**: 2025-11-27  
**Status**: Draft  
**Input**: User description: "Change the 'required' schema definition attribute item to 'presence' with valid values being 'required', 'preferred', and 'optional' with 'optional' being the default. Update the validator so that missing data results in an error if 'required', a warning if 'preferred', and nothing if 'optional'."

## Clarifications

### Session 2025-11-27
- Q: Does `presence: required` imply the value must be non-null? → A: No. `presence` only checks key existence; nullability is handled by type definition (e.g. `type: string | null`).
- Q: How should the legacy `required` attribute be handled? → A: Strict validation. The schema parser must treat `required` as an invalid attribute and raise a schema parsing error.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define Required Field (Priority: P1)

As a schema author, I want to define a field as strictly required so that data failing to include this field is rejected as invalid.

**Why this priority**: This is the core validation functionality replacing the previous boolean `required` attribute. Without this, the schema cannot enforce mandatory fields.

**Independent Test**: Can be fully tested by creating a schema with `presence: required` and validating data that is missing that field.

**Acceptance Scenarios**:

1. **Given** a schema with a field `id` defined with `presence: required`, **When** validating a data object `{ "id": 123 }`, **Then** the validation succeeds with no errors.
2. **Given** a schema with a field `id` defined with `presence: required`, **When** validating a data object `{ "name": "test" }` (missing `id`), **Then** the validation fails with an error indicating `id` is missing.

---

### User Story 2 - Define Preferred Field (Priority: P2)

As a schema author, I want to define a field as preferred so that users are warned when it is missing, but the data is still considered valid.

**Why this priority**: This introduces new capability for "soft" requirements, allowing for better data quality guidance without blocking processing.

**Independent Test**: Can be tested by creating a schema with `presence: preferred` and validating data that is missing that field.

**Acceptance Scenarios**:

1. **Given** a schema with a field `description` defined with `presence: preferred`, **When** validating a data object `{ "description": "text" }`, **Then** the validation succeeds with no warnings.
2. **Given** a schema with a field `description` defined with `presence: preferred`, **When** validating a data object `{}` (missing `description`), **Then** the validation succeeds but reports a warning indicating `description` is missing.

---

### User Story 3 - Define Optional Field (Priority: P3)

As a schema author, I want fields to be optional by default or explicitly marked as optional so that missing fields do not cause validation noise.

**Why this priority**: Ensures the default behavior is sensible and allows for explicit documentation of optional fields.

**Independent Test**: Can be tested by creating a schema with `presence: optional` or no `presence` attribute.

**Acceptance Scenarios**:

1. **Given** a schema with a field `notes` defined with `presence: optional`, **When** validating a data object `{}` (missing `notes`), **Then** the validation succeeds with no errors or warnings.
2. **Given** a schema with a field `notes` where the `presence` attribute is omitted, **When** validating a data object `{}` (missing `notes`), **Then** the validation succeeds with no errors or warnings (default is optional).

### Edge Cases

- What happens when an invalid value is provided for `presence` (e.g., `presence: mandatory`)? The schema parser should reject the schema definition.
- What happens when `required` (old attribute) is used? The schema parser MUST reject the schema definition with an error indicating `required` is no longer supported and `presence` should be used instead.
- **Clarification**: `presence: required` checks only for the existence of the key in the data map. It does NOT validate the value itself (e.g., checking for null). Value validation is the responsibility of the `type` attribute.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The YASL schema definition MUST support a `presence` attribute for field definitions.
- **FR-002**: The `presence` attribute MUST accept exactly three values: `required`, `preferred`, and `optional`.
- **FR-003**: If the `presence` attribute is omitted for a field, the system MUST default it to `optional`.
- **FR-004**: The validator MUST report a validation ERROR when a field marked `presence: required` is missing from the data.
- **FR-005**: The validator MUST report a validation WARNING when a field marked `presence: preferred` is missing from the data.
- **FR-006**: The validator MUST NOT report any error or warning when a field marked `presence: optional` (or default) is missing from the data.
- **FR-007**: The validator MUST treat data with WARNINGS as valid (unless configured to treat warnings as errors, but that is out of scope).
- **FR-008**: The schema parser MUST reject schema definitions containing the deprecated `required` attribute.
- **FR-009**: The `presence` check MUST be independent of value validation; a key present with a `null` value satisfies `presence: required` (though it may fail type validation if `null` is not allowed).

### Key Entities *(include if feature involves data)*

- **Schema Field Definition**: The definition of a field within a YASL schema, containing attributes like type and now `presence`.
- **Validation Report**: The output of the validation process, containing a list of Errors and Warnings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of missing fields marked `required` trigger a validation error.
- **SC-002**: 100% of missing fields marked `preferred` trigger a validation warning.
- **SC-003**: 100% of missing fields marked `optional` (or default) trigger no validation messages.
- **SC-004**: Existing schemas can be updated to use `presence` instead of `required` with a clear mapping (`required: true` -> `presence: required`, `required: false` -> `presence: optional`).
