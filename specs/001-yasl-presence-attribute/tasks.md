# Tasks: YASL Presence Attribute

**Feature Branch**: `001-yasl-presence-attribute`
**Spec**: [spec.md](./spec.md)

## Phase 1: Setup

- [ ] T001 Create feature branch `001-yasl-presence-attribute` (already done)
- [ ] T002 Create `specs/001-yasl-presence-attribute/contracts` directory (already done)

## Phase 2: Foundational

- [ ] T003 Update `Property` model in `src/yasl/pydantic_types.py` to replace `required` with `presence`
- [ ] T004 Update `Property` model in `src/yasl/pydantic_types.py` to set default `presence` to `optional`
- [ ] T005 Update `Property` model in `src/yasl/pydantic_types.py` to validate `presence` values (`required`, `preferred`, `optional`)

## Phase 3: User Story 1 - Define Required Field (P1)

**Goal**: Enforce strict requirement for fields marked `presence: required`.

**Independent Test**: Create a schema with `presence: required` and verify validation fails when field is missing.

- [ ] T006 [US1] Create test schema `tests/yasl/data/presence_required.yasl` with a required field
- [ ] T007 [US1] Create valid test data `tests/yasl/data/presence_required_valid.yaml`
- [ ] T008 [US1] Create invalid test data `tests/yasl/data/presence_required_invalid.yaml` (missing field)
- [ ] T009 [US1] Create unit test `tests/yasl/test_presence_required.py` to verify `presence: required` behavior
- [ ] T010 [US1] Update `gen_pydantic_type_models` in `src/yasl/core.py` to handle `presence: required` (make field required in Pydantic model)
- [ ] T011 [US1] Update `gen_pydantic_type_models` in `src/yasl/core.py` to handle `presence: optional` (make field Optional in Pydantic model)
- [ ] T012 [US1] Update `load_and_validate_yasl_with_lines` in `src/yasl/core.py` to reject schemas with legacy `required` attribute

## Phase 4: User Story 2 - Define Preferred Field (P2)

**Goal**: Generate warnings for missing fields marked `presence: preferred`.

**Independent Test**: Create a schema with `presence: preferred` and verify validation succeeds with a warning when field is missing.

- [ ] T013 [US2] Create test schema `tests/yasl/data/presence_preferred.yasl` with a preferred field
- [ ] T014 [US2] Create valid test data `tests/yasl/data/presence_preferred_missing.yaml` (missing field)
- [ ] T015 [US2] Create unit test `tests/yasl/test_presence_preferred.py` to verify `presence: preferred` behavior (warning generation)
- [ ] T016 [US2] Update `gen_pydantic_type_models` in `src/yasl/core.py` to handle `presence: preferred` (make field Optional in Pydantic model)
- [ ] T017 [US2] Update `load_and_validate_data_with_lines` in `src/yasl/core.py` to check for missing `preferred` fields after validation
- [ ] T018 [US2] Update `load_and_validate_data_with_lines` in `src/yasl/core.py` to log warnings for missing `preferred` fields

## Phase 5: User Story 3 - Define Optional Field (P3)

**Goal**: Ensure optional fields (explicit or default) do not cause validation errors or warnings.

**Independent Test**: Create a schema with `presence: optional` and verify validation succeeds silently when field is missing.

- [ ] T019 [US3] Create test schema `tests/yasl/data/presence_optional.yasl` with an optional field
- [ ] T020 [US3] Create valid test data `tests/yasl/data/presence_optional_missing.yaml` (missing field)
- [ ] T021 [US3] Create unit test `tests/yasl/test_presence_optional.py` to verify `presence: optional` behavior (no errors/warnings)
- [ ] T022 [US3] Verify default behavior (no `presence` attribute) acts as `optional` in `tests/yasl/test_presence_optional.py`

## Final Phase: Polish

- [ ] T023 Update `README.md` or documentation to reflect the new `presence` attribute and deprecation of `required`
- [ ] T024 Run full test suite to ensure no regressions
- [ ] T025 Verify all new tests pass

## Dependencies

1.  **Phase 2 (Foundational)** must be completed before any User Story phases.
2.  **Phase 3 (US1)** establishes the core Pydantic model generation logic for `presence`, which US2 and US3 build upon.
3.  **Phase 4 (US2)** adds the post-validation warning logic.
4.  **Phase 5 (US3)** verifies the default/optional behavior.

## Parallel Execution Examples

-   **US1**: T006, T007, T008 (Data creation) can be done in parallel with T009 (Test creation).
-   **US2**: T013, T014 (Data creation) can be done in parallel with T015 (Test creation).
-   **US3**: T019, T020 (Data creation) can be done in parallel with T021 (Test creation).

## Implementation Strategy

1.  **MVP (US1)**: Implement the core `presence` attribute and strict `required` validation. This replaces the existing functionality.
2.  **Enhancement (US2)**: Add the "preferred" warning logic. This is a new capability.
3.  **Verification (US3)**: Ensure the default "optional" behavior works as expected.
