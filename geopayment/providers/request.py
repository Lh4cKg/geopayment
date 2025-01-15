from __future__ import annotations

import logging
import typing as t

import requests
from multidict import CIMultiDict


logger = logging.getLogger(__name__)


class Header(CIMultiDict):
    """
    Container used for request headers.

    It allows for multiple values for a single key in keeping with the HTTP
    spec. Also, all keys are *case in-sensitive*.
    """

    def __getattr__(self, key: str) -> str:
        if key.startswith("_"):
            return self.__getattribute__(key)
        key = key.rstrip("_").replace("_", "-")
        return ",".join(self.getall(key, []))

    def get_all(self, key: str):
        """Convenience method mapped to ``getall()``."""
        return self.getall(key, [])


class Request:

    def __init__(
            self,
            method: str,
            url: str,
            /,
            *,
            params:  t.Dict[str, t.Any] | None = None,
            json: t.Dict[str, t.Any] | None = None,
            data: t.Dict[str, t.Any] | None = None,
            headers: Header = Header(),
            verify: bool = True,
            timeout: t.Tuple[int, int] = (3, 10),
            **kwargs: t.Optional[t.Dict[t.Any, t.Any]],
    ):
        self.method = method.upper()
        self.url = url
        self.params = params
        self.json = json
        self.data = data
        if not isinstance(headers, Header):
            raise TypeError('`headers` must be an instance of `Header`')
        self.headers = headers
        self.allow_redirects = False
        if self.method == 'GET':
            self.allow_redirects = True
        self.verify = verify
        self.timeout = timeout
        self.kwargs = kwargs
        self.verbose = kwargs.pop("verbose", False)

    def __str__(self):
        return (
            'Request('
                f'method={self.method}, url={self.url}, params={self.params}, '
                f'data={self.data}, json={self.json}, headers={self.headers}, '
                f'timeout={self.timeout}, verify={self.verify}'
            ')'
        )

    def send(self) -> requests.Response:
        if self.verbose:
            logger.info(str(self))
        response = requests.request(
            method=self.method,
            url=self.url,
            params=self.params,
            data=self.data,
            json=self.json,
            headers=dict(self.headers),
            allow_redirects=self.allow_redirects,
            timeout=self.timeout,
            verify=self.verify,
            **self.kwargs
        )
        response.headers = Header(response.headers)
        return response

    def set_auth_header(
            self,
            token: str,
            auth_schema: t.Literal['Basic', 'Bearer'] = 'Bearer',
            /
    ) -> None:
        self.headers['Authorization'] = f'{auth_schema} {token}'
