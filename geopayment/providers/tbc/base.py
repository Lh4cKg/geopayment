import inspect
import typing as t
from dataclasses import is_dataclass

from geopayment.providers.request import Header, Request
from geopayment.providers.tbc.models.response import AuthResponse
from geopayment.providers.tbc.models.config import TBCPayConfig
from geopayment.providers.tbc.models.transaction import Command, MessageType
from geopayment.utils.serialize import to_dict


__all__ = ['BaseTBCPayProvider']



class AbstractTBCProvider:
    access: AuthResponse
    ORIGINAL_RESPONSE_KEY = '__response__'

    def __init__(self) -> None:
        assert callable(self.__config__) is False, (
            f'The `{self.__class__.__qualname__}.__config__` '
            f'must be property, not callable function'
        )
        if not is_dataclass(self.__config__) and not isinstance(self.__config__, dict):
            raise TypeError(
                f'The `{self.__class__.__qualname__}.__config__` '
                f'must be type of `dict` or `ProviderConfig`'
            )

    @property
    def __config__(self) -> TBCPayConfig | dict[str, t.Any]:
        raise NotImplementedError


    def get_credentials(self) -> str:
        # TODO
        return

    # helpers

    def _set_original_response(self, f: t.Callable, response) -> None:
        setattr(f.__func__, self.ORIGINAL_RESPONSE_KEY, response)

    def get_original_response(self, f: t.Callable):
        if not callable(f) or not inspect.ismethod(f):
            raise TypeError(f'`f` must be callable function, not {f}')
        return f.__dict__[self.ORIGINAL_RESPONSE_KEY]

    @property
    def auth_headers(self) -> Header:
        header = Header()
        header['Accept'] = 'application/json'
        header['Content-Type'] = 'application/x-www-form-urlencoded'
        header['Authorization'] = f'Basic {self.get_credentials()}'
        return header

    @property
    def form_urlencoded_headers(self) -> Header:
        if not hasattr(self, 'access') or not self.access:
            raise ValueError(
                'Unauthorized request. Use the `get_auth` method for '
                'authorization before performing other operations.'
            )
        header = Header()
        header['Accept'] = 'application/json'
        header['Content-Type'] = 'application/x-www-form-urlencoded'
        header['Authorization'] = f'Bearer {self.access.access_token}'
        return header

    @property
    def api_headers(self) -> Header:
        if not hasattr(self, 'access') or not self.access:
            raise ValueError(
                'Unauthorized request. Use the `get_auth` method for '
                'authorization before performing other operations.'
            )
        header = Header()
        header['Accept'] = 'application/json'
        header['Content-Type'] = 'application/json'
        header['Authorization'] = f'Bearer {self.access.access_token}'
        return header


class BaseTBCPayProvider(AbstractTBCProvider):

    def __init__(self) -> None:
        super().__init__()

        if isinstance(self.__config__, TBCPayConfig):
            self.config = self.__config__
        else:
            self.config = TBCPayConfig(**self.__config__)

    # Transaction Commands

    @property
    def command(self) -> Command:
        return Command()

    @property
    def message_type(self) -> MessageType:
        return MessageType()

    def perform_request(self, data, verify: bool, timeout: tuple[int, int]):
        request = Request(
            'POST',
            self.config.service_url,
            data=to_dict(data),
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        return request.send()
