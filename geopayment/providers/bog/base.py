import uuid
import inspect
import typing as t
from base64 import b64encode

from geopayment.providers.request import Header
from geopayment.providers.bog.models.config import IPayConfig, BOGConfig
from geopayment.providers.bog.models.response import AuthResponse


class AbstractBogProvider:
    access: AuthResponse

    def __init__(self) -> None:
        assert callable(self.__config__) is False, (
            f'The `{self.__class__.__qualname__}.__config__` '
            f'must be property, not callable function'
        )
        if not isinstance(self.__config__, (IPayConfig, BOGConfig, dict)):
            raise TypeError(
                f'The `{self.__class__.__qualname__}.__config__` '
                f'must be type of `dict` or `ProviderConfig`'
            )

    @property
    def __config__(self) -> IPayConfig | BOGConfig | t.Dict[str, t.Any]:
        raise NotImplementedError

    def get_api_url(self) -> str:
        return f'{self.config.api}/{self.config.api_version}'

    def set_api_version(self, v: str, repl='') -> None:
        """
        A convenient way to set the API version for the config object.
        """
        return self.config.set_api_version(v, repl)

    def set_redirect_url(self, url: str) -> None:
        """
        A convenient way to set the redirect url for the config object.
        """
        return self.config.set_redirect_url(url)

    def get_credentials(self) -> str:
        return b64encode(
            f'{self.config.client_id}:{self.config.secret_key}'.encode()
        ).decode('utf-8')

    # helpers

    @property
    def original_response_key(self) -> str:
        return '__response__'

    def _set_original_response(self, f: t.Callable, response) -> None:
        setattr(f.__func__, self.original_response_key, response)

    def get_original_response(self, f: t.Callable):
        if not callable(f) or not inspect.ismethod(f):
            raise TypeError(f'`f` must be callable function, not {f}')
        return f.__dict__[self.original_response_key]

    @property
    def auth_headers(self) -> Header:
        header = Header()
        header['Accept'] = 'application/json'
        header['Content-Type'] = 'application/x-www-form-urlencoded'
        header['Authorization'] = f'Basic {self.get_credentials()}'
        return header

    @property
    def headers_form_urlencoded(self) -> Header:
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
    def headers(self) -> Header:
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


class BaseIPayProvider(AbstractBogProvider):

    def __init__(self) -> None:
        super().__init__()

        if isinstance(self.__config__, IPayConfig):
            self.config = self.__config__
        else:
            self.config = IPayConfig(**self.__config__)

    # IPay APIs

    @property
    def auth_api(self) -> str:
        return f'{self.get_api_url()}/oauth2/token'

    @property
    def checkout_api(self) -> str:
        return f'{self.get_api_url()}/checkout/orders'

    @property
    def refund_api(self) -> str:
        return f'{self.get_api_url()}/checkout/refund'

    @property
    def order_api(self) -> str:
        return f'{self.get_api_url()}/checkout/orders/{{order_id}}'

    @property
    def order_status_api(self) -> str:
        return f'{self.get_api_url()}/checkout/orders/status/{{order_id}}'

    @property
    def payment_api(self) -> str:
        return f'{self.get_api_url()}/checkout/payment/{{order_id}}'

    @property
    def subscription_api(self) -> str:
        return f'{self.get_api_url()}/checkout/payment/subscription'

    @property
    def pre_auth_api(self) -> str:
        return f'{self.get_api_url()}/checkout/payment/{{order_id}}/pre-auth/completion'

    # Instalment APIs

    @property
    def installment_checkout_api(self) -> str:
        return f'{self.get_api_url()}/installment/checkout'

    @property
    def installment_calculate_api(self) -> str:
        return f'{self.get_api_url()}/services/installment/calculate'

    @property
    def installment_order_api(self) -> str:
        return f'{self.get_api_url()}/installment/checkout/{{order_id}}'


class BaseBogProvider(AbstractBogProvider):

    def __init__(self) -> None:
        super().__init__()

        if isinstance(self.__config__, BOGConfig):
            self.config = self.__config__
        else:
            self.config = BOGConfig(**self.__config__)

    @property
    def idempotency_key(self) -> uuid.UUID:
        return uuid.uuid4()

    # BOG APIs

    @property
    def auth_api(self) -> str:
        return self.config.auth_api

    @property
    def checkout_api(self) -> str:
        return f'{self.get_api_url()}/ecommerce/orders'

    @property
    def order_api(self) -> str:
        return f'{self.get_api_url()}/receipt/{{order_id}}'

    @property
    def order_payment_api(self) -> str:
        return f'{self.get_api_url()}/checkout/payment/{{order_id}}'

    @property
    def pre_auth_approve_api(self) -> str:
        return f'{self.get_api_url()}/payment/authorization/approve/{{order_id}}'

    @property
    def pre_auth_reject_api(self) -> str:
        return f'{self.get_api_url()}/payment/authorization/cancel/{{order_id}}'

    @property
    def refund_api(self) -> str:
        return f'{self.get_api_url()}/payment/refund/{{order_id}}'

    @property
    def save_card_api(self) -> str:
        return f'{self.get_api_url()}/orders/{{order_id}}/cards'

    @property
    def subscription_card_api(self) -> str:
        return f'{self.get_api_url()}/orders/{{order_id}}/subscriptions'

    @property
    def delete_card_api(self) -> str:
        return f'{self.get_api_url()}/charges/card/{{order_id}}'

    @property
    def recurrent_payment_api(self) -> str:
        return f'{self.get_api_url()}/ecommerce/orders/{{parent_order_id}}'

    @property
    def subscribe_payment_api(self) -> str:
        return f'{self.get_api_url()}/ecommerce/orders/{{parent_order_id}}/subscribe'
