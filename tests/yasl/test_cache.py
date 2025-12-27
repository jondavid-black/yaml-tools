from enum import Enum

import pytest
from pydantic import BaseModel, Field

from yasl.cache import YaslRegistry


# --- Test Data ---
class Color(Enum):
    RED = "red"
    BLUE = "blue"


class User(BaseModel):
    name: str = Field(description="User's full name")
    age: int
    active: bool = True
    role: Color = Field(default=Color.RED)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


# --- Fixtures ---
@pytest.fixture
def registry():
    reg = YaslRegistry()
    reg.clear_caches()
    return reg


# --- Tests ---


def test_singleton_behavior():
    reg1 = YaslRegistry()
    reg2 = YaslRegistry()
    assert reg1 is reg2


def test_register_and_get_type(registry):
    registry.register_type("User", User, "test_ns")

    # Direct lookup
    assert registry.get_type("User", "test_ns") is User

    # Lookup by name (unique)
    assert registry.get_type("User") is User

    # Lookup non-existent
    assert registry.get_type("NonExistent") is None
    assert registry.get_type("User", "other_ns") is None


def test_register_duplicate_type(registry):
    registry.register_type("User", User, "test_ns")
    with pytest.raises(ValueError, match="Type 'User' already exists"):
        registry.register_type("User", User, "test_ns")


def test_ambiguous_type_lookup(registry):
    class AnotherUser(BaseModel):
        id: int

    registry.register_type("User", User, "ns1")
    registry.register_type("User", AnotherUser, "ns2")

    # Ambiguous lookup should fail
    with pytest.raises(ValueError, match="Ambiguous type name 'User'"):
        registry.get_type("User")

    # Specific lookup should succeed
    assert registry.get_type("User", "ns1") is User
    assert registry.get_type("User", "ns2") is AnotherUser


def test_register_and_get_enum(registry):
    registry.register_enum("Color", Color, "test_ns")

    assert registry.get_enum("Color", "test_ns") is Color
    assert registry.get_enum("Color") is Color
    assert registry.get_enum("NonExistent") is None


def test_export_schema(registry):
    registry.register_enum("Color", Color, "app")
    registry.register_type("User", User, "app")

    yaml_str = registry.export_schema()

    assert "definitions:" in yaml_str
    assert "app:" in yaml_str

    # Check Enum
    assert "enums:" in yaml_str
    assert "Color:" in yaml_str
    assert "- red" in yaml_str
    assert "- blue" in yaml_str

    # Check Type
    assert "types:" in yaml_str
    assert "User:" in yaml_str
    assert "properties:" in yaml_str

    # Check fields
    assert "name:" in yaml_str
    assert "type: str" in yaml_str
    assert "presence: required" in yaml_str  # name is required

    assert "active:" in yaml_str
    assert "type: bool" in yaml_str
    assert "presence: optional" in yaml_str
    assert "default: true" in yaml_str

    assert "role:" in yaml_str
    assert "type: Color" in yaml_str  # Should reference local enum name
    assert "default: red" in yaml_str


def test_export_schema_cross_namespace_refs(registry):
    class Group(BaseModel):
        name: str
        leader: User  # References User from 'users' namespace

    registry.register_enum("Color", Color, "users")
    registry.register_type("User", User, "users")
    registry.register_type("Group", Group, "groups")

    yaml_str = registry.export_schema()

    # Check namespace grouping
    assert "users:" in yaml_str
    assert "groups:" in yaml_str

    # Check reference formatting
    # Since we are in 'groups' namespace, referencing 'User' in 'users' namespace should be 'users.User'
    assert "type: users.User" in yaml_str
