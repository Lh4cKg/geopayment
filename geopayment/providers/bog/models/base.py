from __future__ import annotations

import re
import typing as t
from dataclasses import dataclass, asdict, field

import ujson

API_URL_NORMALIZE_REGEX = re.compile(r'((/(v1|v1/))|/)$')
API_VERSION_NORMALIZE_REGEX = re.compile(r'/')


def dict_factory(result: dict) -> t.Dict[str, t.Any]:
    return {
        k: v for k, v in result
        if v is not None and v != {} and v != [] and v != ()
    }


@dataclass
class BaseModel:

    config: t.ClassVar[t.Dict[str, t.Any]] = {
        'validation': True
    }

    def to_dict(self, dropna: bool = False) -> t.Dict[t.Any, t.Any] | str:
        if dropna:
            return asdict(self, dict_factory=dict_factory)
        return asdict(self)

    def to_json(self, dropna: bool = False) -> t.Dict[t.Any, t.Any] | str:
        if dropna:
            return ujson.dumps(asdict(self, dict_factory=dict_factory))
        return ujson.dumps(asdict(self))

    def __post_init__(self):
        if self.config['validation']:
            # TODO type validation by annotations
            pass


@dataclass
class RedirectUrls:
    fail: str
    success: str


@dataclass
class ProviderConfig(BaseModel):
    client_id: str
    secret_key: str
    api: str
    api_version: str
    redirect_url: str
    auth_url: str | None = None
    callback_url: str | None = None
    redirect_urls: t.Dict[t.Literal['fail', 'success'], str] | RedirectUrls = field(default_factory=dict)
    verbose: bool = False

    def __post_init__(self):
        if not isinstance(self.client_id, str):
            raise ValueError('client_id must be a string')
        if not isinstance(self.secret_key, str):
            raise ValueError('secret_key must be a string')
        if not isinstance(self.api, str):
            raise ValueError('api must be a string')
        if not isinstance(self.api_version, str):
            raise ValueError('api_version must be a string')
        if not isinstance(self.redirect_url, str):
            raise ValueError('redirect_url must be a string')
        if not isinstance(self.verbose, bool):
            raise ValueError('verbose must be a boolean')

        self.api = self.normalize_api_url(self.api)
        self.api_version = self.normalize_api_version(self.api_version)
        if self.redirect_urls and not isinstance(self.redirect_urls, RedirectUrls):
            self.redirect_urls = RedirectUrls(**self.redirect_urls)

    @staticmethod
    def normalize_api_url(url: str, repl='') -> str:
        return API_URL_NORMALIZE_REGEX.sub(repl, url)

    @staticmethod
    def normalize_api_version(v: str, repl='') -> str:
        return API_VERSION_NORMALIZE_REGEX.sub(repl, v)

    def set_api_version(self, v: str, repl='') -> None:
        self.api_version = self.normalize_api_version(v, repl)

    def set_redirect_url(self, url: str) -> None:
        self.redirect_url = url
