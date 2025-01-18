import typing as t
from dataclasses import dataclass, asdict

try:
    import ujson
except ImportError:
    pass

from geopayment.utils.common import (
    serialize_dict_factory,
    dropna_serialize_dict_factory
)


@dataclass
class BaseModel:

    __config__: t.ClassVar[t.Dict[str, t.Any]] = {
        'validation': True
    }

    def to_dict(self, dropna: bool = False) -> t.Dict[t.Any, t.Any]:
        if dropna:
            return asdict(self, dict_factory=dropna_serialize_dict_factory)
        return asdict(self, dict_factory=serialize_dict_factory)

    def to_json(self, dropna: bool = False) -> str:
        if dropna:
            return ujson.dumps(self.to_dict(dropna=dropna))
        return ujson.dumps(self.to_dict())

    def __post_init__(self):
        if self.__config__['validation']:
            # TODO type validation by annotations
            pass
