import logging
from enum import Enum
from types import MappingProxyType
from typing import Any, Optional

from pydantic import BaseModel


class YaslRegistry:
    """
    Singleton registry for YASL type definitions and enumerations.
    Supports registration and lookup by name and optional namespace.
    """

    _instance: Optional["YaslRegistry"] = None

    def __new__(cls) -> "YaslRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_registry()
        return cls._instance

    def _init_registry(self) -> None:
        self.yasl_type_defs: dict[tuple[str, str | None], type[BaseModel]] = {}
        self.yasl_enumerations: dict[tuple[str, str | None], type[Enum]] = {}
        self.unique_values_store: dict[tuple[str, str | None], dict[str, set]] = {}

    def register_type(
        self, name: str, type_def: type[BaseModel], namespace: str
    ) -> None:
        key = (name, namespace)
        log = logging.getLogger("yasl")
        if key in self.yasl_type_defs:
            raise ValueError(f"Type '{name}' already exists in namespace '{namespace}'")
        self.yasl_type_defs[key] = type_def
        log.debug(f"Registered type '{name}' in namespace '{namespace}'")

    def get_types(self) -> dict[tuple[str, str | None], type[BaseModel]]:
        # Return a read-only view of the registered types
        return MappingProxyType(self.yasl_type_defs)

    def get_type(
        self,
        name: str,
        namespace: str | None = None,
        default_namespace: str | None = None,
    ) -> type[BaseModel] | None:
        log = logging.getLogger("yasl")
        log.debug(
            f"Looking up type '{name}' in namespace '{namespace}' with default namespace '{default_namespace}'"
        )
        if namespace is not None:
            key = (name, namespace)
            if key in self.yasl_type_defs:
                return self.yasl_type_defs[key]
            return None
        matches = [v for (n, ns), v in self.yasl_type_defs.items() if n == name]
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]
        elif default_namespace is not None:
            log.debug(
                f"Trying default namespace '{default_namespace}' for type '{name}'"
            )
            key = (name, default_namespace)
            if key in self.yasl_type_defs:
                return self.yasl_type_defs[key]
        raise ValueError(
            f"Ambiguous type name '{name}': found in multiple namespaces {matches}. Specify a namespace."
        )

    def register_enum(self, name: str, enum_def: type[Enum], namespace: str) -> None:
        log = logging.getLogger("yasl")
        key = (name, namespace)
        if key in self.yasl_enumerations:
            raise ValueError(f"Enum '{name}' already exists in namespace '{namespace}'")
        self.yasl_enumerations[key] = enum_def
        log.debug(f"Registered enum '{name}' in namespace '{namespace}'")

    def get_enum_names(self) -> list[tuple[str, str | None]]:
        return [(n, ns) for (n, ns) in self.yasl_enumerations.keys()]

    def get_enum(
        self,
        name: str,
        namespace: str | None = None,
        default_namespace: str | None = None,
    ) -> type[Enum] | None:
        log = logging.getLogger("yasl")
        log.debug(
            f"Looking up enum '{name}' in namespace '{namespace}' with default namespace '{default_namespace}'"
        )
        if namespace is not None:
            key = (name, namespace)
            if key in self.yasl_enumerations:
                return self.yasl_enumerations[key]
            return None
        matches = [v for (n, ns), v in self.yasl_enumerations.items() if n == name]
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]
        elif default_namespace is not None:
            key = (name, default_namespace)
            if key in self.yasl_enumerations:
                return self.yasl_enumerations[key]
        raise ValueError(
            f"Ambiguous enum name '{name}': found in multiple namespaces {matches}. Specify a namespace."
        )

    def register_unique_value(
        self, type_name: str, property_name: str, value: Any, type_namespace: str = None
    ) -> None:
        if (type_name, type_namespace) not in self.unique_values_store:
            self.unique_values_store[type_name, type_namespace] = {}
        if property_name not in self.unique_values_store[type_name, type_namespace]:
            self.unique_values_store[type_name, type_namespace][property_name] = set()
        if value in self.unique_values_store[type_name, type_namespace][property_name]:
            raise ValueError(
                f"Duplicate unique value '{value}' for property '{property_name}' in type '{type_name}'"
            )
        self.unique_values_store[type_name, type_namespace][property_name].add(value)

    def unique_value_exists(
        self, type_name: str, property_name: str, value: Any, type_namespace: str = None
    ) -> bool:
        if type_namespace is None:
            matches = [
                (tn, ns)
                for (tn, ns) in self.unique_values_store.keys()
                if tn == type_name
            ]
            if not matches:
                return False
            if len(matches) == 1:
                type_namespace = matches[0][1]
            else:
                raise ValueError(
                    f"Ambiguous type name '{type_name}': found in multiple namespaces. Specify a namespace."
                )

        return (
            (type_name, type_namespace) in self.unique_values_store
            and property_name in self.unique_values_store[type_name, type_namespace]
            and value
            in self.unique_values_store[type_name, type_namespace][property_name]
        )

    def clear_caches(self) -> None:
        """Clean up global stores after validation."""
        self.unique_values_store.clear()
        self.yasl_type_defs.clear()
        self.yasl_enumerations.clear()


# Singleton instance
yasl_registry = YaslRegistry()
