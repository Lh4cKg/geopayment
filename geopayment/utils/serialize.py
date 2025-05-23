import typing as t
from decimal import Decimal
from dataclasses import asdict

try:
    import ujson
    dumps = ujson.dumps
except ImportError:
    from json import dumps


def default_serializer(result: dict) -> t.Dict[str, t.Any]:
    return {
        k: str(v) if isinstance(v, Decimal) else v for k, v in result
    }


def dropna_serializer(result: dict) -> t.Dict[str, t.Any]:
    """
    null values are dropped.
    """
    return {
        k: str(v) if isinstance(v, Decimal) else v for k, v in result
        if v or isinstance(v, bool)
    }


def to_dict(cls, dropna: bool = False) -> dict[t.Any, t.Any]:
    if dropna:
        return asdict(cls, dict_factory=dropna_serializer)
    return asdict(cls, dict_factory=default_serializer)


def to_json(cls, dropna: bool = False) -> str:
    return dumps(to_dict(cls, dropna=dropna))
