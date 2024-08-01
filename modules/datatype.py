"""
CSV LowTypes:
Number, String

SuperCSV HighTypes:
Integer, Float, String, Boolean, Array(LIST), DateTime, Object(JSON), Null(NONE)

BaseTypes:
Python builtin types like int, str, float etc.
"""
from abc import ABC, abstractmethod
from datetime import datetime
import json


type Number = int | float
type LowType = str | Number | bool | dict


class _HighType[BaseT](ABC):
    _base_type: BaseT

    def __repr__(self) -> str:
        return f"<_HighType: {self.__class__.__name__} (BaseT: {self._base_type})>"

    @abstractmethod
    def encode(data: BaseT) -> LowType:
        """ Convert data to savable string. """
        ...

    @abstractmethod
    def decode(data: LowType) -> BaseT:
        """ Convert saved string to real type.  """
        ...



class Integer[BaseT: int](_HighType):
    _base_type = int

    def encode(data: Number) -> LowType:
        return Integer._base_type(data)

    def decode(data: Number) -> BaseT:
        return Integer._base_type(data)


class Float[BaseT: float](_HighType):
    _base_type = float

    def encode(data: Number) -> LowType:
        return Float._base_type(data)

    def decode(data: Number) -> BaseT:
        return Float._base_type(data)


class String[BaseT: str](_HighType):
    _base_type = str

    def encode(data: str) -> LowType:
        return String._base_type(data)

    def decode(data: str) -> BaseT:
        return String._base_type(data)


class Boolean[BaseT: bool](_HighType):
    _base_type = bool

    def encode(data: bool) -> LowType:
        return "1" if data else "0"

    def decode(data: str) -> BaseT:
        return data == "1"


class Array[BaseT: list](_HighType):
    _base_type = list
    _base_types_translation = {
        bool: "B",
        str: "S",
        int: "I",
        float: "F",
    }
    _items_sep = "\00"

    def encode(data: list[LowType]) -> LowType:
        chain = ""
        for item in data:
            item_t = type(item)
            if item_t not in Array._base_types_translation.keys():
                raise ValueError(f"Cannot encode item: <{item_t}> ({item}). Data type not supported.")

            dt_prefix = Array._base_types_translation.get(item_t)
            chain += f"{dt_prefix}::{str(item)}{Array._items_sep}"

        return chain

    def decode(data: str) -> BaseT:
        seq = []

        for item in data.split(Array._items_sep):
            if not item:
                continue
            type_repr, value = item.split("::", 1)

            for basetype, prefix in Array._base_types_translation.items():
                if prefix == type_repr:
                    break
            else:                
                raise ValueError(f"Cannot decode item: <{item}> invalid type: {type_repr}")

            seq.append(basetype(value))

        return seq


class DateTime[BaseT: datetime](_HighType):
    _base_type = datetime

    def encode(data: datetime) -> LowType:
        return str(data.timestamp())

    def decode(data: str) -> BaseT:
        return datetime.fromtimestamp(float(data))


class Object[BaseT: dict](_HighType):
    _base_type = dict

    def encode(data: dict) -> LowType:
        return json.dumps(data)

    def decode(data: str) -> BaseT:
        return json.loads(data)



ANNOTATIONS_TABLE = {
    "interger": Integer,
    "int": Integer,
    "i": Integer,
    "float": Float,
    "f": Float,
    "string": String,
    "str": String,
    "s": String,
    "boolean": Boolean,
    "bool": Boolean,
    "b": Boolean,
    "array": Array,
    "arr": Array,
    "a": Array,
    "object": Object,
    "obj": Object,
    "o": Object,
}

