import re
import types
import typing as t
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict, is_dataclass, MISSING, Field
from decimal import Decimal, ROUND_UP

try:
    import ujson
    dumps = ujson.dumps
except ImportError:
    from json import dumps

from geopayment.utils.common import (
    serialize_dict_factory,
    dropna_serialize_dict_factory
)


@dataclass
class BaseModel:

    __config__: t.ClassVar[dict[str, bool]] = {
        'validation': False
    }

    def to_dict(self, dropna: bool = False) -> dict[t.Any, t.Any]:
        if dropna:
            return asdict(self, dict_factory=dropna_serialize_dict_factory)
        return asdict(self, dict_factory=serialize_dict_factory)

    def to_json(self, dropna: bool = False) -> str:
        if dropna:
            return dumps(self.to_dict(dropna=dropna))
        return dumps(self.to_dict())

    def __post_init__(self):
        if self.__config__['validation']:
            cls = type(self)
            annotations = t.get_type_hints(cls)
            for field, type_hint in annotations.items():
                if field == '__config__':
                    continue

                dc_field = self.__dataclass_fields__[field]
                value = self.__dict__[field]
                if not value:
                    if self.__none_type_validation(type_hint) or self.__default_validation(dc_field):
                        continue
                    raise ValueError(
                        f'The `{cls.__qualname__}.{field}` is required.'
                    )

                if isinstance(type_hint, (types.GenericAlias, t._GenericAlias)):
                    self.__generic_alias_validation(
                        field=field, value=value, type_hint=type_hint
                    )
                elif isinstance(type_hint, types.UnionType):
                    for union_arg in t.get_args(type_hint):
                        is_dc = is_dataclass(union_arg)
                        if is_dc:
                            if not isinstance(value, union_arg):
                                self.__setattr__(field, union_arg(**value))
                            break
                        elif isinstance(union_arg, (types.GenericAlias, t._GenericAlias)):
                            self.__generic_alias_validation(
                                field=field, value=value, type_hint=union_arg
                            )
                            break
                        elif union_arg is Decimal:
                            self.__decimal_validation(field, value)
                            break
                        elif union_arg is uuid.UUID:
                            self.__setattr__(field, uuid.UUID(value))
                            break
                elif isinstance(value, type_hint):
                    continue
                elif is_dataclass(type_hint) and isinstance(value, dict):
                    self.__setattr__(field, type_hint(**value))
                elif type_hint is Decimal:
                    self.__decimal_validation(field, value)
                elif type_hint is int:
                    self.__int_validation(field, value)
                elif type_hint is float:
                    self.__float_validation(field, value)
                elif type_hint is str:
                    self.__setattr__(field, str(value))
                elif type_hint is uuid.UUID:
                    self.__setattr__(field, uuid.UUID(value))
                elif (
                        isinstance(type_hint, t._LiteralGenericAlias)
                        and self.__literal_validation(value, type_hint)
                ):
                    self.__setattr__(field, value)
                elif type_hint is datetime:
                    self.__datetime_validation(field, value)

    # Helper functions

    @staticmethod
    def __default_validation(field: Field) -> bool:
        return not field.default_factory is MISSING or not field.default is MISSING

    def __int_validation(self, field: str, value: t.Any) -> t.Literal[True]:
        try:
            self.__setattr__(field, int(value))
            return True
        except (ValueError, TypeError):
            raise TypeError(
                f'The value `{value}` cannot be converted to an `int` object.'
            )

    def __float_validation(self, field: str, value: t.Any) -> t.Literal[True]:
        try:
            self.__setattr__(field, float(value))
            return True
        except (ValueError, TypeError):
            raise TypeError(
                f'The value `{value}` cannot be converted to an `float` object.'
            )

    def __decimal_validation(self, field: str, value: t.Any) -> t.Literal[True]:
        if not isinstance(value, (int, float)) and not self.__numeric_validation(value):
            raise TypeError(
                f'The value `{value}` cannot be converted to a `Decimal` object.'
            )
        self.__setattr__(field, Decimal(value).quantize(Decimal('.00'), rounding=ROUND_UP))
        return True

    @staticmethod
    def __none_type_validation(type_hint: t.Generic) -> bool:
        for th in t.get_args(type_hint):
            if th is type(None):
                return True
        return False

    @staticmethod
    def __numeric_validation(value: t.Any) -> bool:
        return bool(re.match(r'(\d+\.\d+|\d+)', value))

    def __datetime_validation(self, field, value: str) -> bool:
        try:
            if 'T' in value and 'Z' in value:
                dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            self.__setattr__(field, dt)
        except ValueError:
            return False
        return True

    @staticmethod
    def __literal_validation(value: t.Any, type_hint: t.Generic) -> t.Literal[True]:
        choices = t.get_args(type_hint)
        if value not in choices:
            raise TypeError(
                f'The specified value `{value}` must be one of {choices}.'
            )
        return True

    def __generic_alias_validation(self, *, field, value, type_hint) -> t.Literal[True]:
        origin = type_hint.__origin__
        if origin is list:
            for arg in t.get_args(type_hint):
                is_dc = is_dataclass(arg)
                if is_dc:
                    if not isinstance(value, list):
                        raise TypeError(
                            f'The value `{value}` must be list object.'
                        )
                    values = []
                    for i in value:
                        if not isinstance(i, dict):
                            raise TypeError(
                                f'The {arg.__qualname__} value `{i}` must be dict object.'
                            )
                        values.append(arg(**i))
                    self.__setattr__(field, values)
                    break
                elif isinstance(arg, (t._UnionGenericAlias, types.GenericAlias, t._GenericAlias)):
                    for union_arg in t.get_args(arg):
                        is_dc = is_dataclass(union_arg)
                        if is_dc:
                            if not isinstance(value, list):
                                raise TypeError(
                                    f'The value `{value}` must be list object.'
                                )
                            values = []
                            for i in value:
                                if not isinstance(i, dict):
                                    raise TypeError(
                                        f'The {union_arg.__qualname__} value `{i}` must be dict object.'
                                    )
                                values.append(union_arg(**i))
                            self.__setattr__(field, values)
                            break
                elif isinstance(arg, types.UnionType):
                    for union_arg in t.get_args(arg):
                        is_dc = is_dataclass(union_arg)
                        if is_dc:
                            if isinstance(value, dict):
                                self.__setattr__(field, union_arg(**value))
                            elif isinstance(value, list):
                                value = [union_arg(**i) for i in value]
                                self.__setattr__(field, value)
        elif origin is t.Union:
            for arg in t.get_args(type_hint):
                if isinstance(arg, t._LiteralGenericAlias):
                    self.__literal_validation(value, arg)
                    break
                elif is_dataclass(arg):
                    if not isinstance(value, dict):
                        raise TypeError(
                            f'The value `{value}` must be dict object.'
                        )
                    self.__setattr__(field, arg(**value))
                    break
                else:
                    raise ValueError('unsupported union type.')
        elif origin is t.Literal:
            self.__literal_validation(value, type_hint)
        else:
            raise TypeError('unsupported type.')
        return True


@dataclass
class ValidationModel(BaseModel):

    __config__: t.ClassVar[dict[str, bool]] = {
        'validation': True
    }
