# Data Model: YASL Presence Attribute

**Feature**: `001-yasl-presence-attribute`

## Schema Updates

### `Property` (in `src/yasl/pydantic_types.py`)

The `Property` class defines the attributes of a field in a YASL schema.

**Changes:**
-   **Remove**: `required: bool | None`
-   **Add**: `presence: str | None` (Valid values: `required`, `preferred`, `optional`. Default: `optional`)

**Updated Definition:**

```python
class Property(YASLBaseModel):
    # ... existing fields ...
    type: str
    description: str | None = None
    # required: bool | None = True  <-- REMOVED
    presence: Literal["required", "preferred", "optional"] | None = "optional" # <-- ADDED
    unique: bool | None = False
    default: Any | None = None
    # ... existing fields ...
```

## Validation Logic

### `load_and_validate_data_with_lines` (in `src/yasl/core.py`)

The validation logic will be updated to handle the `presence` attribute.

**Logic:**

1.  **Schema Parsing**:
    -   When parsing the YASL schema, `presence` is read.
    -   If `presence` is `required`, the generated Pydantic field is **required** (not `Optional`).
    -   If `presence` is `preferred` or `optional`, the generated Pydantic field is **Optional**.

2.  **Data Validation**:
    -   `model(**data)` is called.
    -   If a `required` field is missing, Pydantic raises a `ValidationError` (ERROR).

3.  **Post-Validation Warning Check**:
    -   After successful Pydantic validation, iterate through the schema properties.
    -   If a property has `presence="preferred"`:
        -   Check if the property name is in `instance.model_fields_set`.
        -   If NOT in `model_fields_set`, log a **WARNING**.
