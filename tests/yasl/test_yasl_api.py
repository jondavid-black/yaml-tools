import pytest
import yaml
from pydantic import ValidationError

from yasl.core import (
    load_data,
    load_schema,
)

try:
    from tests.yasl.schema_data import TODO_YASL
except ImportError:
    # Fallback for when running tests directly or in different environments
    try:
        from schema_data import TODO_YASL
    except ImportError:
        # Last resort relative import
        from .schema_data import TODO_YASL


def test_load_and_validate_yasl_with_dictionary():
    """Test loading and validating YASL schema and YAML data using dictionary input."""

    # 1. Load the YASL schema as a dictionary
    yasl_data = yaml.safe_load(TODO_YASL)

    # 2. Validate the YASL schema
    yasl_model = load_schema(yasl_data)
    assert yasl_model is not None

    # 3. Create sample YAML data (matching the schema) as a dictionary
    yaml_data_dict = {
        "task_list": {
            "task1": {
                "description": "My first task",
                "owner": "Alice",
                "complete": False,
            },
            "task2": {"description": "Another task", "complete": True},
        }
    }

    # 4. Validate the YAML data against the loaded schema
    #    The TODO_YASL schema defines types in the 'dynamic' namespace.
    #    The root type for the data is 'list_of_tasks'
    validated_model = load_data(
        schema_name="list_of_tasks",
        schema_namespace="dynamic",
        yaml_data=yaml_data_dict,
    )

    assert validated_model is not None
    assert validated_model.task_list["task1"].description == "My first task"
    assert validated_model.task_list["task1"].owner == "Alice"
    assert validated_model.task_list["task2"].complete is True


def test_yasl_validation_errors():
    """Test that YASL schema validation correctly identifies errors."""

    # 1. Schema with missing required fields
    invalid_yasl_data = {
        "definitions": {
            "my_ns": {
                "types": {
                    "my_type": {
                        # Missing properties
                    }
                }
            }
        }
    }

    # Validation should fail (return None or raise ValidationError depending on implementation)
    # Based on core.py load_and_validate_yasl, it raises ValueError if validation fails
    with pytest.raises(
        (ValueError, ValidationError)
    ):  # Catching general exception as it might be Pydantic validation error
        load_schema(invalid_yasl_data)

    # 2. Schema with invalid structure
    invalid_structure_yasl = {"definitions": "this should be a dict"}
    with pytest.raises((ValueError, ValidationError)):
        load_schema(invalid_structure_yasl)


def test_yaml_data_validation_errors():
    """Test that YAML data validation correctly identifies errors against the schema."""

    # Setup: Load a valid schema. We need to clear registry first because previous tests might have registered it.
    from yasl.cache import YaslRegistry

    YaslRegistry().clear_caches()

    yasl_data = yaml.safe_load(TODO_YASL)
    load_schema(yasl_data)

    # 1. Data with missing required field
    yaml_data_missing_field = {
        "task_list": {
            "task1": {
                # Missing description
                "owner": "Alice",
                "complete": False,
            }
        }
    }

    result = load_data(
        schema_name="list_of_tasks",
        schema_namespace="dynamic",
        yaml_data=yaml_data_missing_field,
    )
    assert result is None

    # 2. Data with incorrect type
    yaml_data_wrong_type = {
        "task_list": {
            "task1": {
                "description": 12345,  # Should be str
                "complete": False,
            }
        }
    }

    result = load_data(
        schema_name="list_of_tasks",
        schema_namespace="dynamic",
        yaml_data=yaml_data_wrong_type,
    )
    assert result is None

    # 3. Data with extra fields (schema forbids extra by default)
    yaml_data_extra_field = {
        "task_list": {
            "task1": {
                "description": "Task",
                "complete": False,
                "extra_field": "Not allowed",
            }
        }
    }

    result = load_data(
        schema_name="list_of_tasks",
        schema_namespace="dynamic",
        yaml_data=yaml_data_extra_field,
    )
    assert result is None
