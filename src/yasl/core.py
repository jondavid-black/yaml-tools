# validate_config_with_lines.py
import logging
from yasl.pydantic_types import (
    Enumeration,
    TypeDef,
    YaslRoot,
    YASLBaseModel
)
from yasl.validators import property_validator_factory, type_validator_factory
from ruamel.yaml import YAML, YAMLError
from pydantic import (
    BaseModel, 
    ValidationError, 
    create_model, 
    StrictBool,
    PositiveInt,
    NegativeInt,
    NonPositiveInt,
    NonNegativeInt,
    StrictInt,
    PositiveFloat,
    NegativeFloat,
    NonPositiveFloat,
    NonNegativeFloat,
    StrictFloat,
    FiniteFloat,
    StrictStr,
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    UUID6,
    UUID7,
    UUID8,
    FilePath,
    DirectoryPath,
    Base64Bytes,
    Base64Str,
    Base64UrlBytes,
    Base64UrlStr,
    AnyUrl,
    AnyHttpUrl,
    HttpUrl,
    AnyWebsocketUrl,
    WebsocketUrl,
    FileUrl,
    FtpUrl,
    PostgresDsn,
    CockroachDsn,
    AmqpDsn,
    RedisDsn,
    MongoDsn,
    KafkaDsn,
    NatsDsn,
    MySQLDsn,
    MariaDBDsn,
    ClickHouseDsn,
    SnowflakeDsn,
    EmailStr,
    NameEmail,
    IPvAnyAddress,
)
from enum import Enum
from typing import Dict, Type, List, Optional, Tuple, Any, Callable
import datetime
from pathlib import Path
import json
from io import StringIO
import sys
import os
import tomllib
import traceback

# --- Logging Setup ---
class YamlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        yaml = YAML()
        log_dict = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        stream = StringIO()
        log_list = []
        log_list.append(log_dict)
        yaml.dump(log_list, stream)
        return stream.getvalue().strip()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_dict = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        return json.dumps(log_dict)
    
def setup_logging(disable: bool, verbose: bool, quiet: bool, logfmt: str, stream: StringIO = sys.stdout):
    logger = logging.getLogger()
    logger.handlers.clear()
    if disable:
        logger.disabled = True
        return
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO
    logger.setLevel(level)
    handler = logging.StreamHandler(stream)
    if logfmt == "json":
        handler.setFormatter(JsonFormatter())
    elif logfmt == "yaml":
        handler.setFormatter(YamlFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

# --- YASL Models and Validation Logic ---

def yasl_version() -> str:
    try:
        pyproject_path = os.path.join(os.path.dirname(__file__), "../../pyproject.toml")
        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)
        return pyproject["project"]["version"]
    except Exception:
        # fallback to old version if pyproject.toml is missing or malformed
        return "Unknown due to internal error reading pyproject.toml"

def yasl_eval(yasl_schema: str, yaml_data: str, model_name: str = None, disable_log: bool = False, quiet_log: bool = False, verbose_log: bool = False, log_fmt: str = "text", log_stream: StringIO = sys.stdout) -> Optional[BaseModel]:

    setup_logging(disable=disable_log, verbose=verbose_log, quiet=quiet_log, logfmt=log_fmt, stream=log_stream)
    log = logging.getLogger("yasl")
    log.debug(f"YASL Version:  {yasl_version()}")
    log.debug(f"YASL Schema:   {yasl_schema}")
    log.debug(f"YAML Data:    {yaml_data}")
    yasl = load_and_validate_yasl_with_lines(yasl_schema)
    if yasl is None:
        log.error("❌ YASL schema validation failed. Exiting.")
        return None
    if model_name is None:
        yaml_loader = YAML(typ="rt")
        with open(yaml_data, "r") as f:
            data = yaml_loader.load(f)
        root_keys: List[str] = list(data.keys())
        for type_def in yasl.types or []:
            type_def_root_keys: List[str] = [k for k in type_def.properties]
            if type_def.root and all(k.name in root_keys for k in type_def_root_keys):
                model_name = type_def.name
                log.debug(f"Auto-detected root model: '{model_name}'")
                break
            else:
                log.debug(f"Model '{type_def.name}' with root keys {type_def_root_keys} is not a match for root keys {root_keys}")
    from yasl import yasl_type_defs, yasl_enumerations
    if model_name not in yasl_type_defs:
        log.error(f"❌ Error: Model '{model_name}' not found in YASL schema definitions.")
        return None
    model = yasl_type_defs[model_name]
    log.debug(f"Using model '{model_name}' for data validation.")
    data = load_and_validate_data_with_lines(model, yaml_data)
    # clean up global stores after validation
    from yasl.validators import unique_values_store
    unique_values_store.clear()
    yasl_type_defs.clear()
    yasl_enumerations.clear()
    return data

def gen_enum_from_enumeration(enum_def: Enumeration) -> Type[Enum]:
    """
    Dynamically generate a Python Enum class from an Enumeration instance.
    Each value in the Enumeration becomes a member of the Enum.
    """
    from yasl import yasl_enumerations
    enum_members = {value: value for value in enum_def.values}
    enum_cls = Enum(enum_def.name, enum_members)
    if enum_def.namespace:
        enum_cls.__module__ = enum_def.namespace
    yasl_enumerations[enum_def.name] = enum_cls
    return enum_cls


def gen_pydantic_type_models(type_defs: List[TypeDef]):
    """
    Dynamically generate Pydantic model classes from a list of TypeDef instances.
    Each property in the TypeDef becomes a field in the generated model.
    """
    for type_def in type_defs:
        fields: Dict[str, tuple] = {}
        validators: Dict[str, Callable] = {}
        for prop in type_def.properties:
            # Determine type annotation for the property
            # For now, map basic types; extend as needed for complex types
            type_map = {
                "str": str,
                "string": str,
                "date": datetime.date,
                "datetime": datetime.datetime,
                "time": datetime.time,
                "int": int,
                "float": float,
                "bool": bool,
                "path": str,
                "url": str,
                "any": Any,
                "StrictBool": StrictBool,
                "PositiveInt": PositiveInt,
                "NegativeInt": NegativeInt,
                "NonPositiveInt": NonPositiveInt,
                "NonNegativeInt": NonNegativeInt,
                "StrictInt": StrictInt,
                "PositiveFloat": PositiveFloat,
                "NegativeFloat": NegativeFloat,
                "NonPositiveFloat": NonPositiveFloat,
                "NonNegativeFloat": NonNegativeFloat,
                "StrictFloat": StrictFloat,
                "FiniteFloat": FiniteFloat,
                "StrictStr": StrictStr,
                "UUID1": UUID1,
                "UUID3": UUID3,
                "UUID4": UUID4,
                "UUID5": UUID5,
                "UUID6": UUID6,
                "UUID7": UUID7,
                "UUID8": UUID8,
                "FilePath": FilePath,
                "DirectoryPath": DirectoryPath,
                "Base64Bytes": Base64Bytes,
                "Base64Str": Base64Str,
                "Base64UrlBytes": Base64UrlBytes,
                "Base64UrlStr": Base64UrlStr,
                "AnyUrl": AnyUrl,
                "AnyHttpUrl": AnyHttpUrl,
                "HttpUrl": HttpUrl,
                "AnyWebsocketUrl": AnyWebsocketUrl,
                "WebsocketUrl": WebsocketUrl,
                "FileUrl": FileUrl,
                "FtpUrl": FtpUrl,
                "PostgresDsn": PostgresDsn,
                "CockroachDsn": CockroachDsn,
                "AmqpDsn": AmqpDsn,
                "RedisDsn": RedisDsn,
                "MongoDsn": MongoDsn,
                "KafkaDsn": KafkaDsn,
                "NatsDsn": NatsDsn,
                "MySQLDsn": MySQLDsn,
                "MariaDBDsn": MariaDBDsn,
                "ClickHouseDsn": ClickHouseDsn,
                "SnowflakeDsn": SnowflakeDsn,
                "EmailStr": EmailStr,
                "NameEmail": NameEmail,
                "IPvAnyAddress": IPvAnyAddress,
            }
            type_lookup = prop.type
            is_list = False
            if type_lookup.endswith("[]"):
                type_lookup = prop.type[:-2]
                is_list = True

            from yasl import (yasl_type_defs, yasl_enumerations)
            if type_lookup in yasl_enumerations:
                py_type = yasl_enumerations[type_lookup]
            elif type_lookup in yasl_type_defs:
                py_type = yasl_type_defs[type_lookup]
            elif type_lookup in type_map:
                py_type = type_map[type_lookup]
            elif type_lookup.startswith("ref(") and type_lookup.endswith(")"):
                ref_target = type_lookup[4:-1]
                type_name, property_name = ref_target.split('.', 1)
                
                target_type = next((t for t in type_defs if t.name == type_name), None)
                if not target_type:
                    raise ValueError(f"Referenced type '{type_name}' for property '{prop.name}' not found in type definitions")
                else:
                    target_prop = next((p for p in target_type.properties if p.name == property_name), None)
                    if not target_prop:
                        raise ValueError(f"Referenced property '{property_name}' in type '{type_name}' not found for property '{prop.name}'")
                    else:
                        if not target_prop.unique:
                            raise ValueError(f"Referenced property '{type_name}.{property_name}' must be unique to be used as a reference for property '{type_def.name}.{prop.name}'")
                        else:
                            py_type = str
            else:
                raise ValueError(f"Unknown type '{prop.type}' for property '{prop.name}'")

            if is_list:
                py_type = List[py_type]

            if not prop.required:
                py_type = Optional[py_type]

            default = (
                prop.default
                if prop.default is not None
                else (None if not prop.required else ...)
            )
            fields[prop.name] = (py_type, default)
            validators[f"{prop.name}__validator"] = property_validator_factory(type_def, prop)
        validators["__validate__"] = type_validator_factory(type_def)
        model = create_model(
            type_def.name,
            __base__=YASLBaseModel,
            __module__=type_def.namespace or None,
            __validators__=validators,
            __config__={"extra": "forbid"},
            **fields,
        )
        # Store the generated model in the global registry
        from yasl import yasl_type_defs
        yasl_type_defs[type_def.name] = model


# --- Helper function to find the line number ---
def get_line_for_error(data, loc: Tuple[str, ...]) -> Optional[int]:
    """Traverse the ruamel.yaml data to find the line number for an error location."""
    current_data = data
    try:
        for key in loc:
            current_data = current_data[key]
        # .lc is the line/column accessor in ruamel.yaml
        return current_data.lc.line + 1
    except (KeyError, IndexError, AttributeError):
        # Fallback if we can't find the exact key (e.g., for a missing key)
        # We can try to get the line of the parent object.
        parent_data = data
        for key in loc[:-1]:
            parent_data = parent_data[key]
        try:
            return parent_data.lc.line + 1
        except AttributeError:
            return None


# --- Main schema validation logic ---
def load_and_validate_yasl_with_lines(path: str) -> YaslRoot:
    log = logging.getLogger("yasl")
    log.debug(f"--- Attempting to validate schema '{path}' ---")
    try:
        yaml_loader = YAML(typ="rt")
        with open(path, "r") as f:
            data = yaml_loader.load(f)
        yasl = YaslRoot(**data)
        if yasl is None:
            raise ValueError("Failed to parse YASL schema from data {data}")
        if yasl.imports is not None:
            for imp in yasl.imports:
                imp_path = imp
                if not Path(imp_path).exists():
                    # try relative to current schema file
                    imp_path = Path(path).parent / imp
                    if not imp_path.exists():
                        raise FileNotFoundError(f"Import file '{imp}' not found")
                log.debug(f"Importing additional schema: {imp}  - resolved to {imp_path}")
                imported_yasl = load_and_validate_yasl_with_lines(imp_path)
                if not imported_yasl:
                    raise ValueError(f"Failed to import YASL schema from '{imp}'")
        for enum in yasl.enums or []:
            # must setup enums before types to support enum validation
            log.debug(f"Evaluating enum: {enum.name}")
            gen_enum_from_enumeration(enum)
        if yasl.types is not None:
            gen_pydantic_type_models(yasl.types)
            # setup_yasl_validators(type_def)
        log.debug("✅ YASL schema validation successful!")
        return yasl
    except FileNotFoundError:
        log.error(f"❌ Error: File not found at '{path}'")
        return None
    except ValidationError as e:
        log.error(f"❌ YASL schema validation of {path} failed with {len(e.errors())} error(s):")
        for error in e.errors():
            line = get_line_for_error(data, error["loc"])
            path_str = " -> ".join(map(str, error["loc"]))
            if line:
                log.error(f"  - Line {line}: '{path_str}' -> {error['msg']}")
            else:
                log.error(f"  - Location '{path_str}' -> {error['msg']}")
        return None
    except Exception as e:
        log.error(f"❌ An unexpected error occurred: {type(e)} - {e}")
        traceback.print_exc()
        return None


# --- Main data validation logic ---
def load_and_validate_data_with_lines(
    model: type, path: str
) -> Any:
    log = logging.getLogger("yasl")
    log.debug(f"--- Attempting to validate data '{path}' ---")
    try:
        yaml_loader = YAML(typ="rt")
        with open(path, "r") as f:
            data = yaml_loader.load(f)

    except FileNotFoundError:
        log.error(f"❌ Error: File not found at '{path}'")
        return None
    except YAMLError as e:
        log.error(f"❌ Error: YAML error while parsing data '{path}'\n  - {e}")
        return None
    except ValueError as e:
        log.error(f"❌ Error: value error while parsing data '{path}'\n  - {e}")
        return None
    except Exception as e:
        log.error(f"❌ An unexpected error occurred: {type(e)} - {e}")
        traceback.print_exc()
        return None
    try:
        result = model(**data)
        if result is None:
            raise ValueError(f"Failed to parse data from {data}")
        log.info("✅ YAML data validation successful!")
        return result
    except ValidationError as e:
        log.error(f"❌ Validation failed with {len(e.errors())} error(s):")
        for error in e.errors():
            line = get_line_for_error(data, error["loc"])
            path_str = " -> ".join(map(str, error["loc"]))
            if line:
                log.error(f"  - Line {line}: '{path_str}' -> {error['msg']}")
            else:
                log.error(f"  - Location '{path_str}' -> {error['msg']}")
        return None
    except Exception as e:
        log.error(f"❌ An unexpected error occurred: {type(e)} - {e}")
        traceback.print_exc()
        return None
