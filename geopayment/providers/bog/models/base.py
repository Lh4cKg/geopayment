from __future__ import annotations

import re
import typing as t
from dataclasses import dataclass, field
from geopayment.providers.models import BaseModel, ValidationModel


__all__ = ['IPayConfig', 'BOGConfig']


API_URL_NORMALIZE_REGEX = re.compile(r'((/(v1|v1/))|/)$')
API_VERSION_NORMALIZE_REGEX = re.compile(r'/')


@dataclass
class RedirectUrls:
    fail: str
    success: str


@dataclass
class IPayConfig(BaseModel):
    client_id: str
    secret_key: str
    redirect_url: str
    api: str | None = None
    api_version: str | None = None
    callback_url: str | None = None
    verbose: bool = False

    def __post_init__(self):
        self.api = self.normalize_api_url(self.api or self.default_api)
        self.api_version = self.normalize_api_version(
            self.api_version or self.default_api_version
        )

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

    @property
    def default_api(self) -> str:
        return 'https://ipay.ge/opay/api/'

    @property
    def default_api_version(self) -> str:
        return 'v1'


@dataclass
class BOGConfig(ValidationModel):
    client_id: str
    secret_key: str
    redirect_url: str | None = None
    api: str | None = None
    api_version: str | None = None
    auth_api: str | None = None
    callback_url: str | None = None
    redirect_urls: RedirectUrls | dict[t.Literal['fail', 'success'], str] = field(default_factory=dict)
    verbose: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.api = self.normalize_api_url(self.api or self.default_api)
        self.api_version = self.normalize_api_version(
            self.api_version or self.default_api_version
        )
        if self.auth_api is None:
            self.auth_api = self.default_auth_api

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

    @property
    def default_api(self) -> str:
        return 'https://api.bog.ge/payments'

    @property
    def default_auth_api(self) -> str:
        return 'https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token'

    @property
    def default_api_version(self) -> str:
        return 'v1'
