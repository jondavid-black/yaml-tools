# from .cli import main
from typing import Dict, Type
from enum import Enum

from pydantic import BaseModel
from yasl.core import yasl_eval, yasl_version

# yasl type and enum registries
yasl_type_defs: Dict[
    str, Type[BaseModel]
] = {}  # Global registry for type definitions to support ref validation
yasl_enumerations: Dict[
    str, Type[Enum]
] = {}  # Global registry for enums to support enum validation

__all__ = [
    # "main",
    "yasl_eval",
    "yasl_version",
    yasl_type_defs,
    yasl_enumerations,
]