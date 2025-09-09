# validate_config_with_lines.py
import logging
from wsgiref import validate
from ruamel.yaml import YAML
from pydantic import BaseModel, ValidationError, create_model, field_validator
from enum import Enum
from typing import Dict, Type, List, Optional, Tuple, Any, Callable
from functools import partial
import re
import datetime

# yasl validator functions

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
def date_format_validator(cls, value: str, format: str):
    try:
        datetime.strptime(value, format)
    except ValueError:
        raise ValueError(f"Date '{value}' does not match format '{format}'")
    return value

def date_before_validator(cls, value: str, before: str):
    if value >= before:
        raise ValueError(f"Date '{value}' must be before '{before}'")
    return value

def date_after_validator(cls, value: str, after: str):
    if value <= after:
        raise ValueError(f"Date '{value}' must be after '{after}'")
    return value

# uri validators
def uri_regex_validator(cls, value: str, regex: str):
    if not re.fullmatch(regex, value):
        raise ValueError(f"Value '{value}' does not match pattern '{regex}'")
    return value

def uri_exists_validator(cls, value: str, exists: bool):

    def is_uri_accessible(value: str) -> bool:
        # TODO Implement the logic to check if the URI is accessible
        return True
    
    if exists and not is_uri_accessible(value):
        raise ValueError(f"URI '{value}' must exist")
    return value

def uri_protocol_validator(cls, value: str, protocols: List[str]):
    if not any(value.startswith(protocol) for protocol in protocols):
        raise ValueError(f"URI '{value}' must start with one of {protocols}")
    return value

def is_dir_validator(cls, value: str, is_dir: bool):

    def is_uri_directory(cls, value: str):
        # TODO Implement the logic to check if the URI is a directory
        return True

    if is_dir and not is_uri_directory(value):
        raise ValueError(f"URI '{value}' must be a directory")
    return value

def is_file_validator(cls, value: str, is_file: bool):

    def is_uri_file(value: str) -> bool:
        # TODO Implement the logic to check if the URI is a file
        return True

    if is_file and not is_uri_file(value):
        raise ValueError(f"URI '{value}' must be a file")
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
def any_of_validator(cls, value: Any, allowed_types: List[str]):
    if not any(isinstance(value, eval(t)) for t in allowed_types):
        raise ValueError(f"Value '{value}' must be one of {allowed_types}")
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

def property_validator_factory(property) -> Callable:
    
    validators = []
    # list validators
    if property.list_min is not None:
        validators.append(partial(list_min_validator, bound=property.list_min))
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
        validators.append(partial(exclude_validator, bound=property.exclude))

    # string validators
    if property.str_min is not None:
        validators.append(partial(str_min_validator, bound=property.str_min))
    if property.str_max is not None:
        validators.append(partial(str_max_validator, bound=property.str_max))
    if property.str_regex is not None:
        validators.append(partial(str_regex_validator, bound=property.str_regex))

    # date validators
    if property.date_format is not None:
        validators.append(partial(date_format_validator, bound=property.date_format))
    if property.before is not None:
        validators.append(partial(date_before_validator, bound=property.before))
    if property.after is not None:
        validators.append(partial(date_after_validator, bound=property.after))

    # uri validators
    if property.uri_regex is not None:
        validators.append(partial(uri_regex_validator, bound=property.uri_regex))
    if property.uri_exists is not None:
        validators.append(partial(uri_exists_validator, bound=property.uri_exists))
    if property.is_dir is not None:
        validators.append(partial(is_dir_validator, bound=property.is_dir))
    if property.is_file is not None:
        validators.append(partial(is_file_validator, bound=property.is_file))
    if property.uri_protocol is not None:
        validators.append(partial(uri_protocol_validator, bound=property.uri_protocol))

    # any validator
    if property.any_of is not None:
        validators.append(partial(any_of_validator, bound=property.any_of))

    # ref validators
    if property.ref_exists is not None:
        validators.append(partial(ref_exists_validator, bound=property.ref_exists))
    if property.ref_multi is not None:
        validators.append(partial(ref_multi_validator, bound=property.ref_multi))
    if property.ref_filters is not None:
        validators.append(partial(ref_filters_validator, bound=property.ref_filters))

    def multi_validator(cls, value):
        for validator in validators:
            value = validator(value)
        return value
    return field_validator(property.name)(multi_validator)

# --- YASL Pydantic Models ---
class Enumeration(BaseModel):
    name: str
    description: Optional[str] = None
    namespace: Optional[str] = None
    values: List[str]

    model_config = {
        "extra": "forbid"
    }

def gen_enum_from_enumeration(enum_def: Enumeration) -> Type[Enum]:
    """
    Dynamically generate a Python Enum class from an Enumeration instance.
    Each value in the Enumeration becomes a member of the Enum.
    """
    enum_members = {value: value for value in enum_def.values}
    enum_cls = Enum(enum_def.name, enum_members)
    if enum_def.namespace:
        enum_cls.__module__ = enum_def.namespace
    return enum_cls

class RefFilter(BaseModel):
    target: str
    value: str

    model_config = {
        "extra": "forbid"
    }

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

    # date constraints
    date_format: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None

    # uri constraints
    uri_regex: Optional[str] = None
    uri_exists: Optional[bool] = None
    is_dir: Optional[bool] = None
    is_file: Optional[bool] = None
    uri_protocol: Optional[str] = None
    uri_reachable: Optional[bool] = None

    # any constraints
    any_of: Optional[List[str]] = None

    # ref constraints
    ref_exists: Optional[bool] = None
    ref_multi: Optional[bool] = None
    ref_filters: Optional[List[RefFilter]] = None

    model_config = {
        "extra": "forbid"
    }

class IfThen(BaseModel):
    eval: str
    value: List[str]
    present: List[str]
    absent: List[str]

    model_config = {
        "extra": "forbid"
    }

class Validator(BaseModel):
    only_one: Optional[List[str]] = None
    at_least_one: Optional[List[str]] = None
    if_then: Optional[IfThen] = None

    model_config = {
        "extra": "forbid"
    }

class TypeDef(BaseModel):
    name: str
    namespace: Optional[str] = None
    description: Optional[str] = None
    root: Optional[bool] = False
    properties: List[Property]
    validators: Optional[Validator] = None

    model_config = {
        "extra": "forbid"
    }

def type_validator_factory(model: TypeDef) -> Callable:

    validators = []
    if model.validators is not None:
        if model.validators.only_one is not None:
            validators.append(partial(only_one_validator, fields=model.validators.only_one))
        if model.validators.at_least_one is not None:
            validators.append(partial(at_least_one_validator, fields=model.validators.at_least_one))
        if model.validators.if_then is not None:
            validators.append(partial(if_then_validator, if_then=model.validators.if_then.dict()))

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
            "int": int,
            "num": float,
            "bool": bool,
            "any": Any,
        }
        py_type = type_map.get(prop.type, Any)
        default = prop.default if prop.default is not None else (None if not prop.required else ...)
        fields[prop.name] = (py_type, default)
        validators[prop.name] = property_validator_factory(prop)
    validators["__validate__"] = type_validator_factory(type_def)
    model = create_model(
        type_def.name,
        __base__=BaseModel,
        __module__=type_def.namespace or None,
        __validators__=validators,
        **fields
    )
    return model

class ProjectAttribute(BaseModel):
    quiet: Optional[bool] = False
    verbose: Optional[bool] = False
    logfmt: Optional[str] = "text"
    ssl_verify: Optional[bool] = True
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    warn_as_error: Optional[bool] = False

    model_config = {
        "extra": "forbid"
    }

class ProjectImport(BaseModel):
    source: str
    version: Optional[str] = None

    model_config = {
        "extra": "forbid"
    }

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    license: Optional[str] = None
    version: Optional[str] = None
    keywords: Optional[List[str]] = None
    attributes: Optional[ProjectAttribute] = None
    content: Optional[str] = None
    imports: Optional[List[ProjectImport]] = None

    model_config = {
        "extra": "forbid"
    }

class YASL(BaseModel):
    project: Optional[Project] = None
    types: Optional[List[TypeDef]] = None
    enums: Optional[List[Enumeration]] = None

    model_config = {
        "extra": "forbid"
    }

# --- Helper function to find the line number ---
def get_line_for_error(data, loc: Tuple[str, ...]) -> Optional[int]:
    """Traverse the ruamel.yaml data to find the line number for an error location."""
    current_data = data
    try:
        for key in loc:
            current_data = current_data[key]
        # .lc is the line/column accessor in ruamel.yaml
        return current_data.lc.line + 1
    except (KeyError, IndexError, AttributeError) as e:
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
def load_and_validate_yasl_with_lines(path: str) -> YASL:
    log = logging.getLogger("yasl")
    log.debug(f"--- Attempting to validate schema '{path}' with line numbers ---")
    try:
        yaml_loader = YAML(typ='rt')
        with open(path, 'r') as f:
            data = yaml_loader.load(f)
        yasl = YASL(**data)
        log.debug("✅ YASL schema validation successful!")

        return yasl
    except FileNotFoundError:
        log.error(f"❌ Error: File not found at '{path}'")
    except ValidationError as e:
        log.error(f"❌ Validation failed with {len(e.errors())} error(s):")
        for error in e.errors():
            line = get_line_for_error(data, error['loc'])
            path_str = " -> ".join(map(str, error['loc']))
            if line:
                log.error(f"  - Line {line}: '{path_str}' -> {error['msg']}")
            else:
                log.error(f"  - Location '{path_str}' -> {error['msg']}")
    except Exception as e:
        log.error(f"❌ An unexpected error occurred: {e}")

# --- Main data validation logic ---
def load_and_validate_data_with_lines(model: type, path: str) -> Any:
    log = logging.getLogger("yasl")
    log.debug(f"--- Attempting to validate data '{path}' with line numbers ---")
    try:
        yaml_loader = YAML(typ='rt')
        with open(path, 'r') as f:
            data = yaml_loader.load(f)
        
    except FileNotFoundError as e:
        log.error(f"❌ Error: File not found at '{path}'")

    try:
        result = model(**data)
        log.info("✅ YAML data validation successful!")
        return result
    except ValidationError as e:
        log.error(f"❌ Validation failed with {len(e.errors())} error(s):")
        for error in e.errors():
            line = get_line_for_error(data, error['loc'])
            path_str = " -> ".join(map(str, error['loc']))
            if line:
                log.error(f"  - Line {line}: '{path_str}' -> {error['msg']}")
            else:
                log.error(f"  - Location '{path_str}' -> {error['msg']}")
    except Exception as e:
        log.error(f"❌ An unexpected error occurred: {e}")
