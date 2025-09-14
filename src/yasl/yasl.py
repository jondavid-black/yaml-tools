# validate_config_with_lines.py
import logging
from ruamel.yaml import YAML, YAMLError
from pydantic import (
    BaseModel, 
    ValidationError, 
    create_model, 
    field_validator, 
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
from typing import Dict, Type, List, Optional, Tuple, Any, Callable, Union
from functools import partial
import re
import datetime
from pathlib import Path
from urllib.parse import urlparse
import requests
import json
from io import StringIO
import sys

YASL_VERSION = "0.1.0"

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
    
def setup_logging(disable: bool, verbose: bool, quiet: bool, logfmt: str):
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
    handler = logging.StreamHandler(sys.stdout)
    if logfmt == "json":
        handler.setFormatter(JsonFormatter())
    elif logfmt == "yaml":
        handler.setFormatter(YamlFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

# --- YASL Models and Validation Logic ---

# yasl validator functions
yasl_type_defs: Dict[
    str, Type[BaseModel]
] = {}  # Global registry for type definitions to support ref validation
yasl_enumerations: Dict[
    str, Type[Enum]
] = {}  # Global registry for enums to support enum validation

def yasl_version() -> str:
    return YASL_VERSION

def yasl_eval(yasl_schema: str, yaml_data: str, model_name: str = None, disable_log: bool = False, quiet_log: bool = False, verbose_log: bool = False, log_fmt: str = "text") -> Optional[BaseModel]:
    from yasl import setup_logging, load_and_validate_yasl_with_lines, load_and_validate_data_with_lines

    setup_logging(disable=disable_log, verbose=verbose_log, quiet=quiet_log, logfmt=log_fmt)
    log = logging.getLogger("yasl")
    log.debug(f"YASL Version:  {YASL_VERSION}")
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
    if model_name not in yasl_type_defs:
        log.error(f"❌ Error: Model '{model_name}' not found in YASL schema definitions.")
        return None
    model = yasl_type_defs[model_name]
    log.debug(f"Using model '{model_name}' for data validation.")
    data = load_and_validate_data_with_lines(model, yaml_data)
    return data

class YASLBaseModel(BaseModel):
    def __repr__(self) -> str:
        fields = self.model_dump()  # For Pydantic v2; use self.dict() for v1
        return f"{self.__class__.__name__}({fields})"


# list validation
def list_min_validator(cls, value: List[Any], bound: int):
    if len(value) < bound:
        raise ValueError(f"List must contain at least {bound} items")
    return value


def list_max_validator(cls, value: List[Any], bound: int):
    if len(value) > bound:
        raise ValueError(f"List must contain at most {bound} items")
    return value


# numeric validation
def gt_validator(cls, value, bound):
    if value <= bound:
        raise ValueError(f"Value must be greater than {bound}")
    return value


def ge_validator(cls, value, bound):
    if value < bound:
        raise ValueError(f"Value must be greater than or equal to {bound}")
    return value


def lt_validator(cls, value, bound):
    if value >= bound:
        raise ValueError(f"Value must be less than {bound}")
    return value


def le_validator(cls, value, bound):
    if value > bound:
        raise ValueError(f"Value must be less than or equal to {bound}")
    return value


def exclude_validator(cls, value, excluded_values):
    if value in excluded_values:
        raise ValueError(f"Value must not be one of {excluded_values}")
    return value

def multiple_of_validator(cls, value, bound):
    if value % bound != 0:
        raise ValueError(f"Value must be a multiple of {bound}")
    return value


# string validation
def str_min_validator(cls, value: str, min_length: int):
    if len(value) < min_length:
        raise ValueError(f"String must be at least {min_length} characters long")
    return value


def str_max_validator(cls, value: str, max_length: int):
    if len(value) > max_length:
        raise ValueError(f"String must be at most {max_length} characters long")
    return value


def str_regex_validator(cls, value: str, regex: str):
    if not re.fullmatch(regex, value):
        raise ValueError(f"Value '{value}' does not match pattern '{regex}'")
    return value


# date validators
def date_before_validator(cls, 
                          value: Union[datetime.datetime, datetime.date, datetime.time], 
                          before: Union[datetime.datetime, datetime.date, datetime.time]):
    if not isinstance(value, type(before)):
        raise ValueError(f"Type of value '{type(value)}' does not match type of 'before' '{type(before)}'")
    if value >= before:
        raise ValueError(f"Date '{value}' must be before '{before}'")
    return value


def date_after_validator(cls, 
                         value: Union[datetime.datetime, datetime.date, datetime.time], 
                         after: Union[datetime.datetime, datetime.date, datetime.time]):
    if not isinstance(value, type(after)):
        raise ValueError(f"Type of value '{type(value)}' does not match type of 'after' '{type(after)}'")
    if value <= after:
        raise ValueError(f"Date '{value}' must be after '{after}'")
    return value


# url validators
def url_base_validator(cls, value: str, url_base: str):
    parsed = urlparse(value)
    if url_base != parsed.netloc:
        raise ValueError(f"URL '{value}' does not have a base of '{url_base}'")
    return value


def url_protocol_validator(cls, value: str, protocols: List[str]):
    parsed = urlparse(value)
    if parsed.scheme and parsed.scheme not in protocols:
        raise ValueError(f"URL '{value}' must use one of the protocols {protocols}")
    return value

def url_reachable_valiator(cls, value: str, reachable: bool):
    if reachable:
        try:
            response = requests.head(value, allow_redirects=True, timeout=3)
            if response.status_code >= 400:
                raise ValueError(f"URL '{value}' is not reachable (status {response.status_code})")
        except requests.RequestException as e:
            raise ValueError(f"URL '{value}' is not reachable: {e}")
    return value


def is_dir_validator(cls, value: str, is_dir: bool):
    path = Path(value)
    # Check if the path looks like a directory (ends with separator or no suffix)
    if not(path.suffix == '' or value.endswith(('/', '\\'))):
        raise ValueError(f"Path '{value}' must be a directory")
    return value


def is_file_validator(cls, value: str, is_file: bool):
    path = Path(value)
    # Check if the path looks like a file (does not end with a separator, has a suffix)
    if not(path.suffix != '' and not value.endswith(('/', '\\'))):
        raise ValueError(f"Path '{value}' must be a file")
    return value

def file_ext_validator(cls, value: str, extensions: List[str]):
    path = Path(value)
    # First, ensure it's a file
    is_file_validator(cls, value, True)
    # Check if the file has one of the allowed extensions
    if extensions and path.suffix not in [f".{ext}" if not ext.startswith('.') else ext for ext in extensions] :
        raise ValueError(f"File '{value}' must have one of the following extensions: {extensions}")
    return value

def path_exists_validator(cls, value: str, exists: bool):
    path = Path(value)
    # Check if the path exists on the filesystem
    if exists and not path.exists():
        raise ValueError(f"Path '{value}' must exist on the filesystem")
    return value

# ref validators
def ref_exists_validator(cls, value: Any, exists: bool):
    # TODO figue out reference validation
    pass
    return value


def ref_multi_validator(cls, value: Any, multi: bool):
    # TODO figue out reference validation
    pass
    return value


def ref_filters_validator(cls, value: Any, filters: List[Dict[str, str]]):
    # TODO figue out reference validation
    pass
    return value


# any validator
def any_of_validator(cls, value: Any, any_of: List[str]):
    if not any(isinstance(value, eval(t)) for t in any_of):
        raise ValueError(f"Value '{value}' must be one of {any_of}")
    return value


# type validators
def only_one_validator(cls, values: Dict[str, Any], fields: List[str]):
    data = values.get("properties", {})
    if sum(1 for field in fields if field in data) != 1:
        raise ValueError(f"Exactly one of {fields} must be present")
    return values


def at_least_one_validator(cls, values: Dict[str, Any], fields: List[str]):
    data = values.get("properties", {})
    if sum(1 for field in fields if field in data) < 1:
        raise ValueError(f"At least one of {fields} must be present")
    return values


def if_then_validator(cls, values: Dict[str, Any], if_then: Dict[str, Any]):
    data = values.get("properties", {})
    if if_then.get("eval") and not eval(if_then["eval"], {}, data):
        for field in if_then.get("absent", []):
            if field in data:
                raise ValueError(f"Property '{field}' must not be present")
        for field in if_then.get("present", []):
            if field not in data:
                raise ValueError(f"Property '{field}' must be present")
    return values


# enum validator
def enum_validator(cls, value: Any, values: List[str]):
    str_value = str(value)
    if str_value.split('.')[-1] not in values:
        raise ValueError(f"Value '{value}' must be one of {values}")
    return value


def property_validator_factory(property) -> Callable:
    validators = []
    # list validators
    if property.list_min is not None:
        validators.append((partial(list_min_validator, bound=property.list_min)))
    if property.list_max is not None:
        validators.append(partial(list_max_validator, bound=property.list_max))

    # numeric validators
    if property.gt is not None:
        validators.append(partial(gt_validator, bound=property.gt))
    if property.ge is not None:
        validators.append(partial(ge_validator, bound=property.ge))
    if property.lt is not None:
        validators.append(partial(lt_validator, bound=property.lt))
    if property.le is not None:
        validators.append(partial(le_validator, bound=property.le))
    if property.exclude is not None:
        validators.append(partial(exclude_validator, excluded_values=property.exclude))
    if property.multiple_of is not None:
        validators.append(partial(multiple_of_validator, bound=property.multiple_of))

    # string validators
    if property.str_min is not None:
        validators.append(partial(str_min_validator, min_length=property.str_min))
    if property.str_max is not None:
        validators.append(partial(str_max_validator, max_length=property.str_max))
    if property.str_regex is not None:
        validators.append(partial(str_regex_validator, regex=property.str_regex))

    # date validators
    if property.before is not None:
        validators.append(partial(date_before_validator, before=property.before))
    if property.after is not None:
        validators.append(partial(date_after_validator, after=property.after))

    # path validators
    if property.path_exists is not None:
        validators.append(partial(path_exists_validator, exists=property.path_exists))
    if property.is_dir is not None:
        validators.append(partial(is_dir_validator, is_dir=property.is_dir))
    if property.is_file is not None:
        validators.append(partial(is_file_validator, is_file=property.is_file))
    if property.file_ext is not None:
        validators.append(partial(file_ext_validator, extensions=property.file_ext))

    # uri validators
    if property.url_base is not None:
        validators.append(partial(url_base_validator, url_base=property.url_base))
    if property.url_protocols is not None:
        validators.append(partial(url_protocol_validator, protocols=property.url_protocols))
    if property.url_reachable is not None:
        validators.append(partial(url_reachable_valiator, reachable=property.url_reachable))

    # any validator
    if property.any_of is not None:
        validators.append(partial(any_of_validator, any_of=property.any_of))

    # ref validators
    if property.ref_exists is not None:
        validators.append(partial(ref_exists_validator, exists=property.ref_exists))
    if property.ref_multi is not None:
        validators.append(partial(ref_multi_validator, multi=property.ref_multi))
    if property.ref_filters is not None:
        validators.append(partial(ref_filters_validator, filters=property.ref_filters))

    # enum validators
    if property.type in yasl_enumerations.keys():
        enum_type = yasl_enumerations[property.type]
        validators.append(partial(enum_validator, values=[e.value for e in enum_type]))

    def multi_validator(cls, value):
        for validator in validators:
            value = validator(cls, value)
        return value

    return field_validator(property.name)(multi_validator)


# --- YASL Pydantic Models ---
class Enumeration(BaseModel):
    name: str
    description: Optional[str] = None
    namespace: Optional[str] = None
    values: List[str]

    model_config = {"extra": "forbid"}


def gen_enum_from_enumeration(enum_def: Enumeration) -> Type[Enum]:
    """
    Dynamically generate a Python Enum class from an Enumeration instance.
    Each value in the Enumeration becomes a member of the Enum.
    """
    enum_members = {value: value for value in enum_def.values}
    enum_cls = Enum(enum_def.name, enum_members)
    if enum_def.namespace:
        enum_cls.__module__ = enum_def.namespace
    yasl_enumerations[enum_def.name] = enum_cls
    return enum_cls


class RefFilter(BaseModel):
    target: str
    value: str

    model_config = {"extra": "forbid"}


class Property(BaseModel):
    name: str
    type: str
    namespace: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = True
    unique: Optional[bool] = False
    default: Optional[Any] = None

    # list constraints
    list_min: Optional[int] = None
    list_max: Optional[int] = None

    # numeric constraints
    gt: Optional[float] = None
    ge: Optional[float] = None
    lt: Optional[float] = None
    le: Optional[float] = None
    exclude: Optional[List[float]] = None
    multiple_of: Optional[float] = None
    whole_number: Optional[bool] = False

    # string constraints
    str_min: Optional[int] = None
    str_max: Optional[int] = None
    str_regex: Optional[str] = None

    # date / time constraints
    before: Optional[Union[datetime.date, datetime.datetime, datetime.time]] = None
    after: Optional[Union[datetime.date, datetime.datetime, datetime.time]] = None

    # path constraints
    
    path_exists: Optional[bool] = None
    is_dir: Optional[bool] = None
    is_file: Optional[bool] = None
    file_ext: Optional[List[str]] = None

    # url constraints
    url_base: Optional[str] = None
    url_protocols: Optional[List[str]] = None
    url_reachable: Optional[bool] = False

    # any constraints
    any_of: Optional[List[str]] = None

    # ref constraints
    ref_exists: Optional[bool] = None
    ref_multi: Optional[bool] = None
    ref_filters: Optional[List[RefFilter]] = None

    model_config = {"extra": "forbid"}


class IfThen(BaseModel):
    eval: str
    value: List[str]
    present: List[str]
    absent: List[str]

    model_config = {"extra": "forbid"}


class Validator(BaseModel):
    only_one: Optional[List[str]] = None
    at_least_one: Optional[List[str]] = None
    if_then: Optional[IfThen] = None

    model_config = {"extra": "forbid"}


class TypeDef(BaseModel):
    name: str
    namespace: Optional[str] = None
    description: Optional[str] = None
    root: Optional[bool] = False
    properties: List[Property]
    validators: Optional[Validator] = None

    model_config = {"extra": "forbid"}


def type_validator_factory(model: TypeDef) -> Callable:
    validators = []
    if model.validators is not None:
        if model.validators.only_one is not None:
            validators.append(
                partial(only_one_validator, fields=model.validators.only_one)
            )
        if model.validators.at_least_one is not None:
            validators.append(
                partial(at_least_one_validator, fields=model.validators.at_least_one)
            )
        if model.validators.if_then is not None:
            validators.append(
                partial(if_then_validator, if_then=model.validators.if_then.dict())
            )

    def multi_validator(cls, values):
        for validator in validators:
            values = validator(cls, values)
        return values

    return multi_validator


def gen_pydantic_type_model(type_def: TypeDef) -> Type[BaseModel]:
    """
    Dynamically generate a Pydantic model class from a TypeDef instance.
    Each property in the TypeDef becomes a field in the generated model.
    """
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

        if type_lookup in yasl_enumerations:
            py_type = yasl_enumerations[type_lookup]
        elif type_lookup in yasl_type_defs:
            py_type = yasl_type_defs[type_lookup]
        elif type_lookup in type_map:
            py_type = type_map[type_lookup]
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
        validators[f"{prop.name}__validator"] = property_validator_factory(prop)
    validators["__validate__"] = type_validator_factory(type_def)
    model = create_model(
        type_def.name,
        __base__=YASLBaseModel,
        __module__=type_def.namespace or None,
        __validators__=validators,
        __config__={"extra": "forbid"},
        **fields,
    )
    yasl_type_defs[type_def.name] = model
    return model

class YaslRoot(BaseModel):
    imports: Optional[List[str]] = None
    enums: Optional[List[Enumeration]] = None
    types: Optional[List[TypeDef]] = None

    model_config = {"extra": "forbid"}


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
        for type_def in yasl.types or []:
            log.debug(f"Evaluating type definition: {type_def.name}")
            gen_pydantic_type_model(type_def)
            # setup_yasl_validators(type_def)
        log.debug("✅ YASL schema validation successful!")
        return yasl
    except FileNotFoundError:
        log.error(f"❌ Error: File not found at '{path}'")
    except ValidationError as e:
        log.error(f"❌ YASL schema validation of {path} failed with {len(e.errors())} error(s):")
        for error in e.errors():
            line = get_line_for_error(data, error["loc"])
            path_str = " -> ".join(map(str, error["loc"]))
            if line:
                log.error(f"  - Line {line}: '{path_str}' -> {error['msg']}")
            else:
                log.error(f"  - Location '{path_str}' -> {error['msg']}")
    except Exception as e:
        log.error(f"❌ An unexpected error occurred: {type(e)} - {e}")


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
        log.error(f"❌ An unexpected error [{type(e)}] occurred in parsing yaml data file: {e}")
        return None
    try:
        result = model(**data)
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
        log.error(f"❌ An unexpected error occurred in load_and_validate_data_with_lines: {e}")
        return None
