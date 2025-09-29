# validate_config_with_lines.py
import logging
import traceback
from yasl.pydantic_types import (
    Enumeration,
    TypeDef,
    YaslRoot,
    YASLBaseModel
)
from yasl.validators import property_validator_factory, type_validator_factory
from yasl.cache import yasl_type_defs, yasl_enumerations, clear_caches
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
from typing import Dict, List, Optional, Tuple, Any, Callable
import datetime
from pathlib import Path
import json
from io import StringIO
import sys
import os
import tomllib

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
    
def setup_logging(disable: bool, verbose: bool, quiet: bool, output: str, stream: StringIO = sys.stdout):
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
    if output == "json":
        handler.setFormatter(JsonFormatter())
    elif output == "yaml":
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

def yasl_eval(yasl_schema: str, yaml_data: str, model_name: str = None, disable_log: bool = False, quiet_log: bool = False, verbose_log: bool = False, output: str = "text", log_stream: StringIO = sys.stdout) -> Optional[List[BaseModel]]:

    setup_logging(disable=disable_log, verbose=verbose_log, quiet=quiet_log, output=output, stream=log_stream)
    log = logging.getLogger("yasl")
    log.debug(f"YASL Version - {yasl_version()}")
    log.debug(f"YASL Schema - {yasl_schema}")
    log.debug(f"YAML Data - {yaml_data}")

    yasl_files = []
    if Path(yasl_schema).is_dir():
        for p in Path(yasl_schema).rglob("*.yasl"):
            yasl_files.append(p)
        if not yasl_files:
            log.error(f"❌ No .yasl files found in directory '{yasl_schema}'")
            clear_caches()
            return None
        log.debug(f"Found {len(yasl_files)} .yasl files in directory '{yasl_schema}'")
    else:
        if not Path(yasl_schema).exists():
            log.error(f"❌ YASL schema file '{yasl_schema}' not found")
            clear_caches()
            return None
        yasl_files.append(Path(yasl_schema))

    yaml_files = []
    if Path(yaml_data).is_dir():
        for p in Path(yaml_data).rglob("*.yaml"):
            yaml_files.append(p)
        if not yaml_files:
            log.error(f"❌ No .yaml files found in directory '{yaml_data}'")
            clear_caches()
            return None
        log.debug(f"Found {len(yaml_files)} .yaml files in directory '{yaml_data}'")
    else:
        if not Path(yaml_data).exists():
            log.error(f"❌ YAML data file '{yaml_data}' not found")
            clear_caches()
            return None
        yaml_files.append(Path(yaml_data))

    yasl_results = []
    for yasl_file in yasl_files:
        yasl = load_and_validate_yasl_with_lines(yasl_file)
        if yasl is None:
            log.error("❌ YASL schema validation failed. Exiting.")
            clear_caches()
            return None
        yasl_results.append(yasl)

    results = []
    
    for yaml_file in yaml_files:
        candidate_model_names = []
        if model_name is None:
            yaml_loader = YAML(typ="rt")
            with open(yaml_file, "r") as f:
                data = yaml_loader.load(f)
            root_keys: List[str] = list(data.keys())
            log.debug(f"Auto-detecting schema for YAML root keys in '{yaml_file}'")
            for yasl_result in yasl_results or []:
                for type_name, type_def in yasl_result.types.items() or []:
                    type_def_root_keys: List[str] = [k for k in type_def.properties.keys()]
                    if all(k in type_def_root_keys for k in root_keys):
                        log.debug(f"Auto-detected root model '{type_name}' for YAML file '{yaml_file}'")
                        candidate_model_names.append(type_name)
        else:
            candidate_model_names.append(model_name)

        log.debug(f"Identified candidate model names for '{yaml_file}' - {candidate_model_names}")

        for schema_name in candidate_model_names:
            if schema_name not in yasl_type_defs:
                continue
            model = yasl_type_defs[schema_name]
            log.debug(f"Using schema '{schema_name}' for data validation of {yaml_file}.")
            data = load_and_validate_data_with_lines(model, yaml_file)
            if data is not None:
                results.append(data)
                break
                
        if len(results) == 0:
            log.error(f"❌ Validation failed. Unable to validate data in YAML file {yaml_file}.")
            clear_caches()
            return None

    clear_caches()
    return results

def gen_enum_from_enumerations(enum_defs: Dict[str, Enumeration]):
    """
    Dynamically generate a Python Enum class from an Enumeration instance.
    Each value in the Enumeration becomes a member of the Enum.
    """
    for enum_name, enum_def in enum_defs.items():
        if enum_name in yasl_enumerations:
            raise ValueError(f"Enumeration '{enum_name}' already exists.")
        enum_members = {value: value for value in enum_def.values}
        enum_cls = Enum(enum_name, enum_members)
        if enum_def.namespace:
            enum_cls.__module__ = enum_def.namespace
        yasl_enumerations[enum_name] = enum_cls


def gen_pydantic_type_models(type_defs: Dict[str, TypeDef]):
    """
    Dynamically generate Pydantic model classes from a list of TypeDef instances.
    Each property in the TypeDef becomes a field in the generated model.
    """
    for typedef_name, type_def in type_defs.items():
        if typedef_name in yasl_type_defs:
            raise ValueError(f"Type definition '{typedef_name}' already exists.")
        fields: Dict[str, tuple] = {}
        validators: Dict[str, Callable] = {}
        for prop_name, prop in type_def.properties.items():
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
                "markdown": str,
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
            is_map = False
            if type_lookup.endswith("[]"):
                type_lookup = prop.type[:-2]
                is_list = True

            if type_lookup in yasl_enumerations:
                py_type = yasl_enumerations[type_lookup]
            elif type_lookup in yasl_type_defs:
                py_type = yasl_type_defs[type_lookup]
            elif type_lookup in type_map:
                py_type = type_map[type_lookup]
            elif type_lookup.startswith("map(") and type_lookup.endswith(")"):
                is_map = True
                key, value = type_lookup[4:-1].split(',', 1)
                key = key.strip()
                type_lookup = value.strip()
                # make sure map key is a known type
                if key in list(yasl_enumerations.keys()):
                    key = yasl_enumerations[key]
                elif key in ["str", "string"]:
                    key = str
                elif key == "int":
                    key = int
                else:
                    acceptable_keys = ["str", "string", "int"] + list(yasl_enumerations.keys())
                    raise ValueError(f"Map key type '{key}' for property '{prop_name}' must be one of {acceptable_keys}.")
                
                # if map value is a list, handle that
                map_value_is_list = False
                if type_lookup.endswith("[]"):
                    type_lookup = prop.type[:-2]
                    map_value_is_list = True

                # make sure map value is a known type
                if type_lookup in type_map:
                    py_type = type_map[type_lookup]
                elif type_lookup in yasl_enumerations:
                    py_type = yasl_enumerations[type_lookup]
                elif type_lookup in yasl_type_defs:
                    py_type = yasl_type_defs[type_lookup]
                else:
                    raise ValueError(f"Unknown map value type '{value}' for property '{prop_name}'")
                
                # wrap in list if needed
                if map_value_is_list:
                    py_type = List[py_type]
            elif type_lookup.startswith("ref(") and type_lookup.endswith(")"):
                ref_target = type_lookup[4:-1]
                type_name, property_name = ref_target.split('.', 1)

                target_type = next((t for t in type_defs.keys() if t == type_name), None)
                if not target_type:
                    raise ValueError(f"Referenced type '{type_name}' for property '{prop_name}' not found in type definitions")
                else:
                    target_prop = next((p for p_name, p in type_defs[target_type].properties.items() if p_name == property_name), None)
                    if not target_prop:
                        raise ValueError(f"Referenced property '{property_name}' in type '{type_name}' not found for property '{prop_name}'")
                    else:
                        if not target_prop.unique:
                            raise ValueError(f"Referenced property '{type_name}.{property_name}' must be unique to be used as a reference for property '{typedef_name}.{prop_name}'")
                        else:
                            py_type = str
            else:
                raise ValueError(f"Unknown type '{prop.type}' for property '{prop_name}'")
            
            if is_list and is_map:
                raise ValueError(f"Property '{prop_name}' cannot be both a list and a map")

            if is_list:
                py_type = List[py_type]

            if is_map:
                py_type = Dict[key, py_type]

            if not prop.required:
                py_type = Optional[py_type]

            default = (
                prop.default
                if prop.default is not None
                else (None if not prop.required else ...)
            )
            fields[prop_name] = (py_type, default)
            validators[f"{prop_name}__validator"] = property_validator_factory(typedef_name, type_def, prop_name, prop)
        validators["__validate__"] = type_validator_factory(type_def)
        model = create_model(
            typedef_name,
            __base__=YASLBaseModel,
            __module__=type_def.namespace or None,
            __validators__=validators,
            __config__={"extra": "forbid"},
            **fields,
        )
        # Store the generated model in the global registry
        yasl_type_defs[typedef_name] = model


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
                log.debug(f"Importing additional schema '{imp}' - resolved to '{imp_path}'")
                imported_yasl = load_and_validate_yasl_with_lines(imp_path)
                if not imported_yasl:
                    raise ValueError(f"Failed to import YASL schema from '{imp}'")
        if yasl.enums is not None:
            # must setup enums before types to support enum validation
            # log.debug(f"Evaluating enum - {enum.name}")
            gen_enum_from_enumerations(yasl.enums)
        if yasl.types is not None:
            gen_pydantic_type_models(yasl.types)
            # setup_yasl_validators(type_def)
        log.debug("✅ YASL schema validation successful!")
        return yasl
    except FileNotFoundError:
        log.error(f"❌ Error - YASL schema file not found at '{path}'")
        return None
    except SyntaxError as e:
        log.error(f"❌ Error - Syntax error in YASL schema file '{path}'\n  - {e}")
        return None
    except YAMLError as e:
        log.error(f"❌ Error - YAML error while parsing YASL schema '{path}'\n  - {e}")
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
        log.error(f"❌ An schema error occurred processing '{path}' - {type(e)} - {e}")
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
        log.error(f"❌ Error - File not found at '{path}'")
        return None
    except SyntaxError as e:
        log.error(f"❌ Error - Syntax error in data file '{path}'\n  - {e}")
        return None
    except YAMLError as e:
        log.error(f"❌ Error - YAML error while parsing data '{path}'\n  - {e}")
        return None
    except ValueError as e:
        log.error(f"❌ Error - value error while parsing data '{path}'\n  - {e}")
        return None
    except Exception as e:
        log.error(f"❌ An unexpected error occurred - {type(e)} - {e}")
        # traceback.print_exc()
        return None
    try:
        result = model(**data)
        if result is None:
            log.error(f"❌ Validation failed. Unable to parse data from {json.dumps(data, indent=2)}")
            raise ValueError(f"Failed to parse data from '{path}'")
        log.info(f"✅ YAML '{path}' data validation successful!")
        return result
    except ValidationError as e:
        log.error(f"❌ Validation failed with {len(e.errors())} error(s):")
        for error in e.errors():
            line = get_line_for_error(data, error["loc"])
            path_str = " -> ".join(map(str, error["loc"]))
            if line:
                log.error(f"  - Line {line} - '{path_str}' -> {error['msg']}")
            else:
                log.error(f"  - Location '{path_str}' -> {error['msg']}")
        # traceback.print_exc()
        return None
    except SyntaxError as e:
        # log.error(f"❌ Error: Syntax error in data file '{path}'\n  - {e}")
        log.error(
            f"❌ SyntaxError in file '{path}' "
            f"at line {getattr(e, 'lineno', '?')}, offset {getattr(e, 'offset', '?')} - {getattr(e, 'msg', str(e))}"
        )
        if hasattr(e, "text") and e.text:
            log.error(f"  > {e.text.strip()}")
        # traceback.print_exc()
        return None
    except Exception as e:
        log.error(f"❌ An unexpected error occurred - {type(e)} - {e}")
        # traceback.print_exc()
        return None
