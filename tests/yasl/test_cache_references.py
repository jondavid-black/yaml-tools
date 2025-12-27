from typing import Annotated

import pytest
import yaml
from pydantic import BaseModel

from yasl import load_schema
from yasl.cache import YaslRegistry
from yasl.primitives import ReferenceMarker


@pytest.fixture
def registry():
    reg = YaslRegistry()
    reg.clear_caches()
    return reg


def test_export_schema_with_reference(registry):
    class Customer(BaseModel):
        name: str

    class Order(BaseModel):
        # Reference to Customer.name using Annotated
        customer_ref: Annotated[str, ReferenceMarker("Customer.name")]

    registry.register_type("Customer", Customer, "store")
    registry.register_type("Order", Order, "store")

    yaml_str = registry.export_schema()

    assert "store:" in yaml_str
    assert "Order:" in yaml_str
    assert "customer_ref:" in yaml_str
    assert "type: ref[Customer.name]" in yaml_str


def test_ref_round_trip(registry):
    yasl_schema = """
definitions:
  acme:
    description: Acme Corporation schema definitions.
    types:
      customer:
        description: Information about a customer.
        properties:
          name:
            type: str
            description: The customer's name.
            presence: required
            unique: true
          address:
            type: str
            description: The customer's address.
            presence: optional
      order:
        description: Information about an order.
        properties:
          order_id:
            type: int
            description: The order's unique identifier.
            presence: required
            unique: true
          customer_ref:
            type: ref[customer.name]
            description: Reference to the customer's name.
            presence: required
"""
    yasl_data = yaml.safe_load(yasl_schema)
    load_schema(yasl_data)

    yaml_str = registry.export_schema()

    assert "acme:" in yaml_str
    assert "customer:" in yaml_str
    assert "order:" in yaml_str
    assert "customer_ref:" in yaml_str
    assert "type: ref[customer.name]" in yaml_str
