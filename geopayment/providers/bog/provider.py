from __future__ import annotations

import logging
import inspect
import typing as t
from base64 import b64encode
from decimal import Decimal

from geopayment.providers.bog.models import ProviderConfig
from geopayment.providers.bog.models.request import (
    AuthData,
    CheckoutData,
    RefundData,
    OrderData,
    OrderStatusData,
    OrderPaymentStatusData,
    PreAuthData,
    SubscriptionData
)
from geopayment.providers.bog.models.response import (
    AuthResponse,
    CheckoutResponse,
    ErrorResponse,
    RefundResponse,
    OrderResponse,
    OrderStatusResponse,
    OrderPaymentResponse,
    PreAuthResponse,
    SubscriptionResponse
)
from geopayment.providers.request import Request, Header


__all__ = ['IPayProvider', 'BogProvider']


logger = logging.getLogger(__name__)


class AbstractBogProvider:
    access: AuthResponse

    def __init__(self) -> None:
        assert callable(self.__config__) is False, (
            f'The `{self.__class__.__qualname__}.__config__` '
            f'must be property, not callable function'
        )
        if not isinstance(self.__config__, (ProviderConfig, dict)):
            raise TypeError(
                f'The `{self.__class__.__qualname__}.__config__` '
                f'must be type of `dict` or `ProviderConfig`'
            )

        if isinstance(self.__config__, ProviderConfig):
            self.config = self.__config__
        else:
            self.config = ProviderConfig(**self.__config__)

    @property
    def __config__(self) -> ProviderConfig | t.Dict[str, t.Any]:
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

    # BOG APIs

    @property
    def auth_api(self):
        return f'{self.get_api_url()}/oauth2/token'

    @property
    def checkout_api(self):
        return f'{self.get_api_url()}/checkout/orders'

    @property
    def refund_api(self):
        return f'{self.get_api_url()}/checkout/refund'

    @property
    def order_api(self):
        return f'{self.get_api_url()}/checkout/orders/{{order_id}}'

    @property
    def order_status_api(self):
        return f'{self.get_api_url()}/checkout/orders/status/{{order_id}}'

    @property
    def payment_api(self):
        return f'{self.get_api_url()}/checkout/payment/{{order_id}}'

    @property
    def subscription_api(self):
        return f'{self.get_api_url()}/checkout/payment/subscription'

    @property
    def pre_auth_api(self):
        return f'{self.get_api_url()}/checkout/payment/{{order_id}}/pre-auth/completion'


class BaseBogProvider(AbstractBogProvider):
    pass


class BogProvider(BaseBogProvider):

    def get_auth(
            self,
            *,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> AuthResponse | ErrorResponse:
        """
        Auth api docs: https://api.bog.ge/docs/payments/authentication

        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return: AuthResponse
        """
        request = Request(
            'POST',
            self.config.auth_url,
            data=AuthData().to_dict(),
            headers=self.auth_headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.get_auth, response)
        if response.status_code != 200:
            return ErrorResponse(**response.json())
        result = response.json()
        result['not_before_policy'] = result.pop('not-before-policy', None)
        self.access = AuthResponse(**result)
        return self.access


class IPayProvider(BaseIPayProvider):

    def get_auth(
            self,
            *,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> AuthResponse | ErrorResponse:
        """
        Auth api docs: https://api.bog.ge/docs/ipay/authentication

        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return: AuthResponse
        """
        request = Request(
            'POST',
            self.auth_api,
            data=AuthData().to_dict(),
            headers=self.auth_headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.get_auth, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        self.access = AuthResponse(**response.json())
        return self.access

    def checkout(
            self,
            *,
            items: t.List[t.Dict[str, t.Any]],
            amount: Decimal | str | float | int | None = None,
            currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL',
            intent: t.Literal['AUTHORIZE', 'CAPTURE'] = 'CAPTURE',
            capture_method: t.Literal['AUTOMATIC', 'MANUAL'] = 'AUTOMATIC',
            locale: t.Literal['ka', 'en-US'] = 'ka',
            redirect_url: str | None = None,
            show_shop_order_id_on_extract: bool = False,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> CheckoutResponse | ErrorResponse:
        """
        checkout api docs: https://api.bog.ge/docs/ipay/create-order

        :param amount: Amount to be paid
        :type amount: Decimal or str or float or int
        :param items: The list of products purchased
        :type items: list of dict
        :param currency_code: A payment currency
        :type currency_code: str
        :param intent: Defines which payment method can be used by the customer
        for payment
        :type intent: str
        :param capture_method: Payment method for pre-authorization or immediate payment
        :type capture_method: str
        :param locale: Defines the language of the Online Payment Webpage on
        which a customer will be redirected.
        :type locale: str
        :param redirect_url: A redirection URL for customers after completing
        an online payment.
        :type redirect_url: str
        :param show_shop_order_id_on_extract: Defines what kind of payment info
        will be shown to a customer on an Online Payment Webpage.
        :type show_shop_order_id_on_extract: bool
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return: CheckoutResponse
        """
        if redirect_url is None:
            redirect_url = self.config.redirect_url
        data = CheckoutData(
            amount=amount,
            items=items,
            currency_code=currency_code,
            intent=intent,
            capture_method=capture_method,
            locale=locale,
            redirect_url=redirect_url,
            show_shop_order_id_on_extract=show_shop_order_id_on_extract,
        ).to_json(dropna=True)
        request = Request(
            'POST',
            self.checkout_api,
            data=data,
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.checkout, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return CheckoutResponse(**response.json())

    def refund(
            self,
            *,
            order_id: str,
            amount: Decimal | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> RefundResponse | ErrorResponse:
        """
        refund api docs: https://api.bog.ge/docs/ipay/refund

        :param order_id: Order identifier for refund processing
        :type order_id: str
        :param amount: refund amount
        :param amount: Decimal or str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return: RefundResponse
        """

        request = Request(
            'POST',
            self.checkout_api,
            json=RefundData(
                order_id=order_id,
                amount=amount
            ).to_dict(dropna=True),
            headers=self.headers_form_urlencoded,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.refund, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return RefundResponse(
            status_code=response.status_code,
            text=response.text,
        )

    def order_status(
            self,
            *,
            order_id: str,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> ErrorResponse | OrderStatusResponse:
        """
        orders status api docs: https://api.bog.ge/docs/ipay/get-payment-details

        :param order_id: Order identifier for refund processing
        :type order_id: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """

        request = Request(
            'GET',
            self.order_status_api.format(order_id=order_id),
            json=OrderStatusData(order_id=order_id).to_dict(),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.order_status, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return OrderStatusResponse(**response.json())

    def get_order(
            self,
            *,
            order_id: str,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> ErrorResponse | OrderResponse:
        """
        order api docs: https://api.bog.ge/docs/ipay/get-payment-details

        :param order_id: Order identifier for refund processing
        :type order_id: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """

        request = Request(
            'GET',
            self.order_api.format(order_id=order_id),
            json=OrderData(order_id=order_id).to_dict(),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.get_order, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return OrderResponse(**response.json())

    def order_payment_details(
            self,
            *,
            order_id: str,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> ErrorResponse | OrderPaymentResponse:
        """
        order payment api docs: https://api.bog.ge/docs/ipay/get-payment-details

        :param order_id: Order identifier for refund processing
        :type order_id: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """

        request = Request(
            'GET',
            self.payment_api.format(order_id=order_id),
            json=OrderPaymentStatusData(order_id=order_id).to_dict(),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return OrderPaymentResponse(**response.json())

    def pre_auth_complete(
            self,
            *,
            order_id: str,
            auth_type: t.Literal['FULL_COMPLETE', 'PARTIAL_COMPLETE', 'CANCEL'],
            amount: Decimal | str | int | float | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> ErrorResponse | PreAuthResponse:
        """
        order payment api docs: https://api.bog.ge/docs/ipay/get-payment-details

        :param order_id: Order identifier for refund processing
        :type order_id: str
        :param auth_type: pre-authorization type
        :type auth_type: str
        :param amount: Is needed only in case (PARTIAL_COMPLETE). Should not be
        equal or more than full amount.
        :type amount: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """

        request = Request(
            'POST',
            self.pre_auth_api.format(order_id=order_id),
            json=PreAuthData(
                order_id=order_id,
                auth_type=auth_type,
                amount=amount,
            ).to_dict(dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.pre_auth_complete, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return PreAuthResponse(**response.json())

    def subscription(
            self,
            *,
            order_id: str,
            amount: Decimal | str | int | float,
            currency_code: t.Literal['GEL', 'USD', 'EUR', 'GBP'] = 'GEL',
            shop_order_id: str | None = None,
            purchase_description: str | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> ErrorResponse | SubscriptionResponse:
        """
        recurring payments api docs: https://api.bog.ge/docs/ipay/recurring-payments

        :param order_id: Order identifier for refund processing
        :type order_id: str
        :param amount: Amount for Recurring Payment
        :type amount: Decimal or str
        :param currency_code: a payment supported currency
        :type currency_code: str
        :param shop_order_id: A Payment identifier from merchant
        :type shop_order_id: str
        :param purchase_description: Purchased product description
        :type purchase_description: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """
        request = Request(
            'POST',
            self.pre_auth_api.format(order_id=order_id),
            json=SubscriptionData(
                order_id=order_id,
                amount=amount,
                currency_code=currency_code,
                shop_order_id=shop_order_id,
                purchase_description=purchase_description,
            ).to_dict(dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.pre_auth_complete, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return SubscriptionResponse(**response.json())
