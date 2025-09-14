from functools import partial
from typing import Dict, List, Any, Union, Callable
from pydantic import field_validator, model_validator
import yasl
from pydantic_types import (
    IfThen,
    TypeDef,
)
import datetime
import re
from urllib.parse import urlparse
import requests
from pathlib import Path

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
    if property.type in yasl.yasl_enumerations.keys():
        enum_type = yasl.yasl_enumerations[property.type]
        validators.append(partial(enum_validator, values=[e.value for e in enum_type]))

    def multi_validator(cls, value):
        for validator in validators:
            value = validator(cls, value)
        return value

    return field_validator(property.name)(multi_validator)

# type validators
def only_one_validator(cls, values: Dict[str, Any], fields: List[str]):
    data_keys = [key for key, val in values.model_dump().items() if val is not None]
    if sum(1 for field in fields if field in data_keys) != 1:
        raise ValueError(f"Exactly one of {fields} must be present")
    return values


def at_least_one_validator(cls, values: Dict[str, Any], fields: List[str]):
    data_keys = [key for key, val in values.model_dump().items() if val is not None]
    if sum(1 for field in fields if field in data_keys) < 1:
        raise ValueError(f"At least one of {fields} must be present")
    return values


def if_then_validator(cls, values: Dict[str, Any], if_then: IfThen):
    eval_field = if_then.eval
    eval_value = if_then.value
    present_fields = if_then.present or []
    absent_fields = if_then.absent or []
    values_dict = values.model_dump()
    if eval_field in values_dict:
        eval_value_type = type(values_dict[eval_field])
        typed_eval_value = [eval_value_type(v) for v in eval_value]
        if values_dict[eval_field] in typed_eval_value:
            for field in present_fields:
                if field not in values_dict or values_dict[field] is None:
                    raise ValueError(f"Field '{field}' must be present when '{eval_field}' is in {eval_value}")
            for field in absent_fields:
                if field in values_dict and values_dict[field] is not None:
                    raise ValueError(f"Field '{field}' must be absent when '{eval_field}' is in {eval_value}")
    return values

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
            for item in model.validators.if_then:
                validators.append(
                    partial(if_then_validator, if_then=item)
                )

    @model_validator(mode="after")
    def multi_validator(cls, values):
        for validator in validators:
            values = validator(cls, values)
        return values

    return multi_validator