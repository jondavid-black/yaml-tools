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
from yasl.cache import YaslRegistry
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
    """
    Evaluate YAML data against a YASL schema.

    Args:
        yasl_schema (str): Path to the YASL schema file or directory.
        yaml_data (str): Path to the YAML data file or directory.
        model_name (str, optional): Specific model name to use for validation. If not provided, the model will be auto-detected.
        disable_log (bool): If True, disables all logging output.
        quiet_log (bool): If True, suppresses all output except for errors.
        verbose_log (bool): If True, enables verbose logging output.
        output (str): Output format for logs. Options are 'text', 'json', or 'yaml'. Default is 'text'.
        log_stream (StringIO): Stream to which logs will be written. Default is sys.stdout.

    Returns:
        Optional[List[BaseModel]]: List of validated Pydantic models if validation is successful, None otherwise.
    """

    setup_logging(disable=disable_log, verbose=verbose_log, quiet=quiet_log, output=output, stream=log_stream)
    log = logging.getLogger("yasl")
    log.debug(f"YASL Version - {yasl_version()}")
    log.debug(f"YASL Schema - {yasl_schema}")
    log.debug(f"YAML Data - {yaml_data}")

    registry = YaslRegistry()

    yasl_files = []
    if Path(yasl_schema).is_dir():
        for p in Path(yasl_schema).rglob("*.yasl"):
            yasl_files.append(p)
        if not yasl_files:
            log.error(f"❌ No .yasl files found in directory '{yasl_schema}'")
            registry.clear_caches()
            return None
        log.debug(f"Found {len(yasl_files)} .yasl files in directory '{yasl_schema}'")
    else:
        if not Path(yasl_schema).exists():
            log.error(f"❌ YASL schema file '{yasl_schema}' not found")
            registry.clear_caches()
            return None
        yasl_files.append(Path(yasl_schema))

    yaml_files = []
    if Path(yaml_data).is_dir():
        for p in Path(yaml_data).rglob("*.yaml"):
            yaml_files.append(p)
        if not yaml_files:
            log.error(f"❌ No .yaml files found in directory '{yaml_data}'")
            registry.clear_caches()
            return None
        log.debug(f"Found {len(yaml_files)} .yaml files in directory '{yaml_data}'")
    else:
        if not Path(yaml_data).exists():
            log.error(f"❌ YAML data file '{yaml_data}' not found")
            registry.clear_caches()
            return None
        yaml_files.append(Path(yaml_data))

    yasl_results = []
    for yasl_file in yasl_files:
        yasl = load_and_validate_yasl_with_lines(yasl_file)
        if yasl is None:
            log.error("❌ YASL schema validation failed. Exiting.")
            registry.clear_caches()
            return None
        yasl_results.append(yasl)

    results = []
    
    for yaml_file in yaml_files:
        
        results = load_and_validate_data_with_lines(model_name, yaml_file)
                
        if not results or len(results) == 0:
            log.error(f"❌ Validation failed. Unable to validate data in YAML file {yaml_file}.")
            registry.clear_caches()
            return None

    registry.clear_caches()
    return results

def gen_enum_from_enumerations(namespace: str, enum_defs: Dict[str, Enumeration]):
    """
    Dynamically generate a Python Enum class from an Enumeration instance.
    Each value in the Enumeration becomes a member of the Enum.
    """
    registry = YaslRegistry()
    for enum_name, enum_def in enum_defs.items():
        if registry.get_enum(enum_name, namespace) is not None:
            raise ValueError(f"Enumeration '{namespace}.{enum_name}' already exists.")
        enum_members = {value: value for value in enum_def.values}
        enum_cls = Enum(enum_name, enum_members)
        enum_cls.__module__ = namespace
        registry.register_enum(enum_name, enum_cls, namespace)


def gen_pydantic_type_models(namespace: str, type_defs: Dict[str, TypeDef]):
    """
    Dynamically generate Pydantic model classes from a list of TypeDef instances.
    Each property in the TypeDef becomes a field in the generated model.
    """
    registry = YaslRegistry()
    for typedef_name, type_def in type_defs.items():
        if registry.get_type(typedef_name, namespace) is not None:
            raise ValueError(f"Type definition '{namespace}.{typedef_name}' already exists.")
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
            type_lookup_namespace = None
            is_list = False
            is_map = False
            if type_lookup.endswith("[]"):
                type_lookup = prop.type[:-2]
                is_list = True

            if "ref[" not in type_lookup and "map[" not in type_lookup and "." in type_lookup:
                # likely a ref to another type or enum
                parts = type_lookup.split(".")
                type_lookup = parts[-1]
                type_lookup_namespace = ".".join(parts[:-1])

            if type_lookup in type_map:
                py_type = type_map[type_lookup]
            elif registry.get_enum(type_lookup, type_lookup_namespace, namespace) is not None:
                py_type = registry.get_enum(type_lookup, type_lookup_namespace, namespace)
            elif registry.get_type(type_lookup, type_lookup_namespace, namespace) is not None:
                py_type = registry.get_type(type_lookup, type_lookup_namespace, namespace)
            elif type_lookup.startswith("map[") and type_lookup.endswith("]"):
                is_map = True
                key, value = type_lookup[4:-1].split(',', 1)

                key_type_lookup = key.strip()
                key_type_lookup_namespace = None
                if "." in key_type_lookup:
                    key_type_lookup_namespace, key_type_lookup = key_type_lookup.rsplit(".", 1)
                # make sure map key is a known type
                
                if key in ["str", "string"]:
                    key = str
                elif key == "int":
                    key = int
                elif registry.get_enum(key_type_lookup, key_type_lookup_namespace, namespace) is not None:
                    key = registry.get_enum(key_type_lookup, key_type_lookup_namespace, namespace)
                else:
                    acceptable_keys = ["str", "string", "int"] + registry.get_enum_names()
                    raise ValueError(f"Map key type '{key}' for property '{prop_name}' must be one of {acceptable_keys}.")
                

                value_type_lookup = value.strip()
                value_type_lookup_namespace = None
                # if map value is a list, handle that
                map_value_is_list = False

                if value_type_lookup.endswith("[]"):
                    value_type_lookup = value_type_lookup[:-2]
                    map_value_is_list = True

                # make sure map value is a known type
                if "." in value_type_lookup:
                    value_type_lookup_namespace, value_type_lookup = value_type_lookup.rsplit(".", 1)
                if value_type_lookup in type_map:
                    py_type = type_map[value_type_lookup]
                elif registry.get_enum(value_type_lookup, value_type_lookup_namespace, namespace) is not None:
                    py_type = registry.get_enum(value_type_lookup, value_type_lookup_namespace, namespace)
                elif registry.get_type(value_type_lookup, value_type_lookup_namespace, namespace) is not None:
                    py_type = registry.get_type(value_type_lookup, value_type_lookup_namespace, namespace)
                else:
                    raise ValueError(f"Unknown map value type '{value_type_lookup}' for property '{prop_name}'")
                
                # wrap in list if needed
                if map_value_is_list:
                    py_type = List[py_type]
            elif type_lookup.startswith("ref[") and type_lookup.endswith("]"):
                ref_target = type_lookup[4:-1]
                if "." not in ref_target:
                    raise ValueError(f"Reference '{ref_target}' for property '{prop_name}' must be in the format TypeName.PropertyName or Namespace.TypeName.PropertyName")
                ref_type_name, property_name = ref_target.rsplit('.', 1)
                ref_type_namespace = None
                if "." in ref_type_name:
                    ref_type_namespace, ref_type_name = ref_type_name.rsplit(".", 1)
                target_type = registry.get_type(ref_type_name, ref_type_namespace, namespace)
                if not target_type:
                    raise ValueError(f"Referenced type '{ref_type_name}' for property '{prop_name}' not found in type definitions")
                else:
                    target_prop = next((p for p_name, p in type_defs[target_type.__name__].properties.items() if p_name == property_name), None)
                    if not target_prop:
                        raise ValueError(f"Referenced property '{property_name}' in type '{ref_type_name}' not found for property '{prop_name}'")
                    else:
                        if not target_prop.unique:
                            raise ValueError(f"Referenced property '{ref_type_name}.{property_name}' must be unique to be used as a reference for property '{typedef_name}.{prop_name}'")
                        elif target_prop.type not in type_map:
                            raise ValueError(f"Referenced property '{ref_type_name}.{property_name}' must be a primitive type to be used as a reference for property '{typedef_name}.{prop_name}'")
                        else:
                            py_type = type_map[target_prop.type]
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
            validators[f"{prop_name}__validator"] = property_validator_factory(typedef_name, namespace, type_def, prop_name, prop)
        validators["__validate__"] = type_validator_factory(type_def)
        model = create_model(
            typedef_name,
            __base__=YASLBaseModel,
            __module__=namespace,
            __validators__=validators,
            __config__={"extra": "forbid"},
            **fields,
        )
        # Store the generated model in the global registry
        registry.register_type(typedef_name, model, namespace)


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
        if yasl.metadata is not None:
            log.debug(f"YASL Metadata: {yasl.metadata}")
        for namespace, yasl_item in yasl.definitions.items():
            # generate enums first so enum map keys are known when generating types
            if yasl_item.enums is not None:
                gen_enum_from_enumerations(namespace, yasl_item.enums)
        for namespace, yasl_item in yasl.definitions.items():
            if yasl_item.types is not None:
                gen_pydantic_type_models(namespace, yasl_item.types)
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
        return None


# --- Main data validation logic ---
def load_and_validate_data_with_lines(
    model_name: str, path: str
) -> Any:
    log = logging.getLogger("yasl")
    log.debug(f"--- Attempting to validate data '{path}' ---")
    docs = []
    try:
        yaml_loader = YAML(typ="rt")
        with open(path, "r") as f:
            docs.extend(yaml_loader.load_all(f))

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
        traceback.print_exc()
        return None
    try:
        results = []
        registry = YaslRegistry()
        for data in docs:
            candidate_model_names: List[Tuple[str, Optional[str]]] = []
            if model_name is None:
                root_keys: List[str] = list(data.keys())
                log.debug(f"Auto-detecting schema for YAML root keys in '{path}'")
                yasl_result = registry.get_types()
                for type_id, type_def in yasl_result.items() or []:
                    type_name, type_namespace = type_id
                    type_def_root_keys: List[str] = list(type_def.model_fields.keys())
                    if all(k in type_def_root_keys for k in root_keys):
                        log.debug(f"Auto-detected root model '{type_name}' for YAML file '{path}'")
                        candidate_model_names.append((type_name, type_namespace))
            else:
                registry_item = registry.get_type(model_name)
                if registry_item:
                    candidate_model_names.append((model_name, registry_item.__module__ or None))
                else:
                    candidate_model_names.append((model_name, None))

            log.debug(f"Identified candidate model names for '{path}' - {candidate_model_names}")

            for (schema_name, schema_namespace) in candidate_model_names:
                if registry.get_type(schema_name, schema_namespace) is None:
                    continue
                model = registry.get_type(schema_name, schema_namespace)
                log.debug(f"Using schema '{schema_name}' for data validation of {path}.")
                result = model(**data)
                if result is not None:
                    results.append(result)
                    break
                else:
                    log.debug(f"Data in '{path}' did not validate against schema '{schema_name}'.")
        
        if not results or len(results) == 0:
            log.error(f"❌ No valid schema found to validate data in '{path}'")
            return None
        log.info(f"✅ YAML '{path}' data validation successful!")
        return results
    except ValidationError as e:
        log.error(f"❌ Validation failed with {len(e.errors())} error(s):")
        for error in e.errors():
            line = get_line_for_error(data, error["loc"])
            path_str = " -> ".join(map(str, error["loc"]))
            if line:
                log.error(f"  - Line {line} - '{path_str}' -> {error['msg']}")
            else:
                log.error(f"  - Location '{path_str}' -> {error['msg']}")
        return None
    except SyntaxError as e:
        log.error(
            f"❌ SyntaxError in file '{path}' "
            f"at line {getattr(e, 'lineno', '?')}, offset {getattr(e, 'offset', '?')} - {getattr(e, 'msg', str(e))}"
        )
        if hasattr(e, "text") and e.text:
            log.error(f"  > {e.text.strip()}")
        return None
    except Exception as e:
        log.error(f"❌ An unexpected error occurred - {type(e)} - {e}")
        traceback.print_exc()
        return None
