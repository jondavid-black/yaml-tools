import pytest
from yasl.primitives import PRIMITIVE_TYPE_MAP


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
