import os
import sys
import tempfile
from io import StringIO
import pytest

# Add src to path just like in test_yasl.py
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src/"))
)

from yasl import yasl_eval
from yasl.primitives import PRIMITIVE_TYPE_MAP


def run_eval_command(yaml_data, yasl_schema, model_name, expect_valid):
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = os.path.join(tmpdir, "test.yaml")
        yasl_path = os.path.join(tmpdir, "test.yasl")
        with open(yaml_path, "w") as f:
            f.write(yaml_data)
        with open(yasl_path, "w") as f:
            f.write(yasl_schema)

        test_log = StringIO()
        yasl_model = yasl_eval(
            yasl_path,
            yaml_path,
            model_name,
            verbose_log=True,
            output="text",
            log_stream=test_log,
        )

        if not expect_valid:
            assert yasl_model is None, (
                f"Expected validation failure, but got success. Log:\n{test_log.getvalue()}"
            )
            assert "❌" in test_log.getvalue()
        else:
            assert yasl_model is not None, (
                f"Expected validation success, but got failure. Log:\n{test_log.getvalue()}"
            )
            assert "data validation successful" in test_log.getvalue()


def test_duration_validation():
    duration_type = PRIMITIVE_TYPE_MAP["duration"]
    # Valid duration
    assert duration_type.validate("10 s") == "10 s"
    assert duration_type.validate("2.5 min") == "2.5 min"

    # Invalid unit for duration (using length instead)
    with pytest.raises(ValueError, match="Physical type mismatch"):
        duration_type.validate("10 m")

    # Invalid format
    with pytest.raises(ValueError, match="Invalid quantity"):
        duration_type.validate("not a number")


def test_length_validation():
    length_type = PRIMITIVE_TYPE_MAP["length"]
    # Valid length
    assert length_type.validate("100 m") == "100 m"
    assert length_type.validate("1.5 km") == "1.5 km"

    # Invalid unit for length
    with pytest.raises(ValueError, match="Physical type mismatch"):
        length_type.validate("10 s")


def test_velocity_validation():
    velocity_type = PRIMITIVE_TYPE_MAP["velocity"]
    # Valid velocity
    assert velocity_type.validate("10 m/s") == "10 m/s"
    assert velocity_type.validate("100 km/h") == "100 km/h"

    # Invalid unit
    with pytest.raises(ValueError, match="Physical type mismatch"):
        velocity_type.validate("10 m")


def test_mass_validation():
    mass_type = PRIMITIVE_TYPE_MAP["mass"]
    # Valid mass
    assert mass_type.validate("10 kg") == "10 kg"
    assert mass_type.validate("500 g") == "500 g"

    # Invalid unit
    with pytest.raises(ValueError, match="Physical type mismatch"):
        mass_type.validate("10 s")


def test_temperature_validation():
    temp_type = PRIMITIVE_TYPE_MAP["temperature"]
    # Valid temperature
    assert temp_type.validate("300 K") == "300 K"

    # Note: Astropy treats 'deg_C' as a unit of temperature difference unless specified otherwise,
    # but for simple Quantity validation it usually works if the physical type matches.
    # Let's check Kelvin which is the base unit.

    # Invalid unit
    with pytest.raises(ValueError, match="Physical type mismatch"):
        temp_type.validate("10 m")


# --- YASL Integration Tests ---


def test_yasl_duration_integration():
    yasl_schema = """
definitions:
  main:
    types:
      event:
        properties:
          duration:
            type: duration
"""
    # Valid
    yaml_data_good = """
duration: 10 s
"""
    run_eval_command(yaml_data_good, yasl_schema, "event", True)

    # Invalid unit
    yaml_data_bad = """
duration: 10 m
"""
    run_eval_command(yaml_data_bad, yasl_schema, "event", False)


def test_yasl_length_integration():
    yasl_schema = """
definitions:
  main:
    types:
      trip:
        properties:
          distance:
            type: length
"""
    # Valid
    yaml_data_good = """
distance: 15 km
"""
    run_eval_command(yaml_data_good, yasl_schema, "trip", True)

    # Invalid unit
    yaml_data_bad = """
distance: 15 kg
"""
    run_eval_command(yaml_data_bad, yasl_schema, "trip", False)


def test_yasl_mixed_physical_types():
    yasl_schema = """
definitions:
  main:
    types:
      car:
        properties:
          max_speed:
            type: velocity
          curb_weight:
            type: mass
"""
    yaml_data = """
max_speed: 120 km/h
curb_weight: 1500 kg
"""
    run_eval_command(yaml_data, yasl_schema, "car", True)

    yaml_data_bad = """
max_speed: 120 km
curb_weight: 1500 kg
"""
    run_eval_command(yaml_data_bad, yasl_schema, "car", False)
