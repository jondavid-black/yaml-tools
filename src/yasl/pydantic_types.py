from pydantic import (
    BaseModel,
)
import datetime
from typing import List, Optional, Any, Union


class YASLBaseModel(BaseModel):
    def __repr__(self) -> str:
        fields = self.model_dump()  # For Pydantic v2; use self.dict() for v1
        return f"{self.__class__.__name__}({fields})"

# --- YASL Pydantic Models ---
class Enumeration(BaseModel):
    name: str
    description: Optional[str] = None
    namespace: Optional[str] = None
    values: List[str]

    model_config = {"extra": "forbid"}

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
    no_ref_check: Optional[bool] = None

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
    if_then: Optional[List[IfThen]] = None

    model_config = {"extra": "forbid"}


class TypeDef(BaseModel):
    name: str
    namespace: Optional[str] = None
    description: Optional[str] = None
    properties: List[Property]
    validators: Optional[Validator] = None

    model_config = {"extra": "forbid"}

class YaslRoot(BaseModel):
    imports: Optional[List[str]] = None
    enums: Optional[List[Enumeration]] = None
    types: Optional[List[TypeDef]] = None

    model_config = {"extra": "forbid"}