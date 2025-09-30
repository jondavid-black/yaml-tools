from typing import Any, Dict, List, Type, Tuple, Optional
from enum import Enum
from pydantic import BaseModel

class YaslRegistry:
    """
    Singleton registry for YASL type definitions and enumerations.
    Supports registration and lookup by name and optional namespace.
    """

    _instance: Optional["YaslRegistry"] = None

    def __new__(cls) -> "YaslRegistry":
        if cls._instance is None:
            cls._instance = super(YaslRegistry, cls).__new__(cls)
            cls._instance._init_registry()
        return cls._instance

    def _init_registry(self) -> None:
        self.yasl_type_defs: Dict[Tuple[str, Optional[str]], Type[BaseModel]] = {}
        self.yasl_enumerations: Dict[Tuple[str, Optional[str]], Type[Enum]] = {}
        self.unique_values_store: Dict[Tuple[str, Optional[str]], Dict[str, set]] = {}

    def register_type(self, name: str, type_def: Type[BaseModel], namespace: Optional[str] = None) -> None:
        key = (name, namespace)
        if key in self.yasl_type_defs:
            raise ValueError(f"Type '{name}' already exists in namespace '{namespace}'")
        self.yasl_type_defs[key] = type_def

    def get_type(self, name: str, namespace: Optional[str] = None) -> Optional[Type[BaseModel]]:
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
        raise ValueError(
            f"Ambiguous type name '{name}': found in multiple namespaces. Specify a namespace."
        )

    def register_enum(self, name: str, enum_def: Type[Enum], namespace: Optional[str] = None) -> None:
        key = (name, namespace)
        if key in self.yasl_enumerations:
            raise ValueError(f"Enum '{name}' already exists in namespace '{namespace}'")
        self.yasl_enumerations[key] = enum_def

    def get_enum_names(self) -> List[Tuple[str, Optional[str]]]:
        return [(n, ns) for (n, ns) in self.yasl_enumerations.keys()]

    def get_enum(self, name: str, namespace: Optional[str] = None) -> Optional[Type[Enum]]:
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
        raise ValueError(
            f"Ambiguous enum name '{name}': found in multiple namespaces. Specify a namespace."
        )

    def register_unique_value(self, type_name: str, property_name: str, value: Any, type_namespace: str = None) -> None:
        if (type_name, type_namespace) not in self.unique_values_store:
            self.unique_values_store[type_name, type_namespace] = {}
        if property_name not in self.unique_values_store[type_name, type_namespace]:
            self.unique_values_store[type_name, type_namespace][property_name] = set()
        if value in self.unique_values_store[type_name, type_namespace][property_name]:
            raise ValueError(f"Duplicate unique value '{value}' for property '{property_name}' in type '{type_name}'")
        self.unique_values_store[type_name, type_namespace][property_name].add(value)


    def unique_value_exists(self, type_name: str, property_name: str, value: Any, type_namespace: str = None) -> bool:
        return (type_name, type_namespace) in self.unique_values_store and \
               property_name in self.unique_values_store[type_name, type_namespace] and \
               value in self.unique_values_store[type_name, type_namespace][property_name]

    def clear_caches(self) -> None:
        """Clean up global stores after validation."""
        self.unique_values_store.clear()
        self.yasl_type_defs.clear()
        self.yasl_enumerations.clear()

# Singleton instance
yasl_registry = YaslRegistry()