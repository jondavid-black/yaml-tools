from typing import Dict, Type
from enum import Enum
from pydantic import BaseModel

# yasl type and enum registries
yasl_type_defs: Dict[
    str, Type[BaseModel]
] = {}  # Global registry for type definitions to support ref validation

yasl_enumerations: Dict[
    str, Type[Enum]
] = {}  # Global registry for enums to support enum validation

# unique value store
unique_values_store: Dict[str, Dict[str, set]] = {}

def clear_caches():
    # clean up global stores after validation
    unique_values_store.clear()
    yasl_type_defs.clear()
    yasl_enumerations.clear()
