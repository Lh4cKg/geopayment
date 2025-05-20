import logging
import inspect
import typing as t
import uuid
from base64 import b64encode
from decimal import Decimal

from geopayment.providers.bog.models.config import IPayConfig, BOGConfig
from geopayment.providers.bog.models.installment import (
    InstallmentCheckoutData,
    InstallmentCalculateData,
    InstallmentOrderData,
)
from geopayment.providers.bog.models.request import (
    AuthData,
    CheckoutData,
    RefundData,
    OrderData,
    OrderStatusData,
    OrderPaymentStatusData,
    PreAuthData,
    SubscriptionData,
    OrderCheckoutData,
    OrderPurchaseUnits,
    Basket,
    Delivery,
    RedirectUrls,
    Buyer,
    Config,
    OrderRefundData, SubscribePaymentData, PreAuthPaymentData
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
    SubscriptionResponse,
    CalculateResponse,
    InstallmentOrderResponse,
    OrderPaymentDetailsResponse, BogRefundResponse, RecurrentResponse,
    CheckoutPaymentResponse, BogPreAuthResponse
)
from geopayment.providers.request import Request, Header
from geopayment.utils.common import to_dict, to_json


__all__ = ['IPayProvider', 'BogProvider']


logger = logging.getLogger(__name__)


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
            self.config.auth_api,
            data=to_dict(AuthData()),
            headers=self.auth_headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.get_auth, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        response = response.json()
        self.access = AuthResponse(
            not_before_policy=response.pop('not-before-policy', None),
            **response
        )
        return self.access

    def checkout(
            self,
            *,
            basket: list[Basket | dict[str, t.Any]],
            total_amount: Decimal | float | int,
            callback_url: str | None = None,
            total_discount_amount: Decimal | float | int | None = None,
            delivery_amount: Decimal | float | int | None = None,
            buyer: Buyer | dict[str, str] | None = None,
            config: Config | dict[str, t.Any] | None = None,
            currency: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL',
            capture: t.Literal['automatic', 'manual'] = 'automatic',
            redirect_urls: dict[t.Literal['success', 'fail'], str] | None = None,
            application_type: t.Literal['web', 'mobile'] = None,
            external_order_id: str | None = None,
            payment_method: list[t.Literal[
                'card', 'google_pay', 'apple_pay', 'bog_p2p',
                'bog_loyalty', 'bnpl', 'bog_loan', 'gift_card'
            ]] = 'card',
            ttl: int = 15,
            accept_language: t.Literal['ka', 'en'] = 'ka',
            theme: t.Literal['light', 'dark'] = 'light',
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: tuple[int, int] | int = (3, 10)
    ) -> CheckoutPaymentResponse | ErrorResponse:
        """
        checkout api docs: https://api.bog.ge/docs/payments/standard-process/create-order

        :param basket: The purchase information.
        :param total_amount: The full amount is to be paid.
        :param callback_url: The web address of the business (must be HTTPS),
                            which will be automatically called by the bank upon
                            completion of the payment to provide the business
                            with the payment details (via Callback).
        :param total_discount_amount: The reduced amount in case of payment with
                                      a discount.
        :param currency:
        :param delivery_amount: Information about the delivery service.
        :param buyer: Information about the buyer.
        :param config: Configuration of a specific payment.
        :param capture: Payment method for pre-authorization or immediate payment.
        :param redirect_urls: The business web addresses that customers can be
                              redirected to from the online payment system upon
                              completion of the payment.
        :param application_type: Defines the type of application from which the
                                 order was created.
        :param external_order_id: The payment identifier from the business system
                                 (e.g., the purchase basket identifier).
        :param payment_method: The payment methods that a customer can use to
                               pay for the order. The business must have all the
                               methods it provides here activated.
        :param ttl: Specifies the duration of the order lifespan in minutes.
        :param accept_language: The language of the interface that the customer
                                will see when redirected to the online payment page.
        :param theme: The theme of the interface that the customer will see when
                      redirected to the online payment page.
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :param verify: in which case it controls whether we verify
                       the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
                        before giving up
        :type timeout: int or Tuple[int, int]

        :return: CheckoutResponse
        """
        callback_url = callback_url or self.config.callback_url
        if not callback_url:
            raise ValueError('The `callback_url` parameter is required.')
        if redirect_urls:
            redirect_urls = RedirectUrls(**redirect_urls)
        else:
            redirect_urls = RedirectUrls(
                fail=self.config.redirect_urls.fail,
                success=self.config.redirect_urls.success,
            )
            if redirect_urls is None:
                raise ValueError('The `redirect_urls` parameter is required.')
        delivery = None
        if delivery_amount:
            delivery = Delivery(amount=delivery_amount)
        purchase_units = OrderPurchaseUnits(
            total_amount=total_amount,
            basket=basket,
            total_discount_amount=total_discount_amount,
            currency=currency,
            delivery=delivery
        )
        data = to_dict(
            OrderCheckoutData(
                purchase_units=purchase_units,
                application_type=application_type,
                buyer=buyer,
                config=config,
                capture=capture,
                redirect_urls=redirect_urls,
                callback_url=callback_url,
                external_order_id=external_order_id,
                ttl=ttl,
                payment_method=payment_method,
            ),
            dropna=True
        )
        request = Request(
            'POST',
            self.checkout_api,
            json=data,
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        if accept_language:
            request.headers['Accept-Language'] = accept_language
        if theme:
            request.headers['Theme'] = theme
        response = request.send()
        self._set_original_response(self.checkout, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return CheckoutPaymentResponse(**response.json())

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
            json=to_dict(OrderData(order_id=order_id)),
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
    ) -> OrderPaymentDetailsResponse | ErrorResponse:
        """
        order payment api docs: https://api.bog.ge/docs/payments/standard-process/get-payment-details

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
            self.order_payment_api.format(order_id=order_id),
            json=to_dict(OrderPaymentStatusData(order_id=order_id)),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return OrderPaymentDetailsResponse(**response.json())

    def save_card_recurring(
            self,
            *,
            order_id: str,
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> RecurrentResponse | ErrorResponse:
        """
        save card for recurring api docs: https://api.bog.ge/docs/payments/saved-card/recurrent

        :param order_id: The order identifier for recurring payment
        :type order_id: str
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :type idempotency_key: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """

        request = Request(
            'PUT',
            self.save_card_api.format(order_id=order_id),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return RecurrentResponse(
            http_status=response.status_code,
            message=response.text
        )

    def save_card_subscription(
            self,
            *,
            order_id: str,
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ):
        """
        save card for subscription api docs: https://api.bog.ge/docs/payments/saved-card/offline

        :param order_id: The order identifier for automatic payment
        :type order_id: str
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :type idempotency_key: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """

        request = Request(
            'PUT',
            self.subscription_card_api.format(order_id=order_id),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return RecurrentResponse(
            http_status=response.status_code,
            message=response.text
        )

    def delete_saved_card(
            self,
            *,
            order_id: str,
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> RecurrentResponse | ErrorResponse:
        """
        delete save card api docs: https://api.bog.ge/docs/payments/saved-card/delete

        :param order_id: The order identifier for automatic payment
        :type order_id: str
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :type idempotency_key: str
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return:
        """

        request = Request(
            'PUT',
            self.delete_card_api.format(order_id=order_id),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return RecurrentResponse(
            http_status=response.status_code,
            message=response.text
        )

    def recurring_payment(
            self,
            *,
            parent_order_id: str,
            basket: list[Basket | dict[str, t.Any]],
            total_amount: Decimal | float | int,
            callback_url: str | None = None,
            total_discount_amount: Decimal | float | int | None = None,
            delivery_amount: Decimal | float | int | None = None,
            buyer: Buyer | dict[str, str] | None = None,
            config: Config | dict[str, t.Any] | None = None,
            currency: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL',
            capture: t.Literal['automatic', 'manual'] = 'automatic',
            redirect_urls: dict[
                               t.Literal['success', 'fail'], str] | None = None,
            application_type: t.Literal['web', 'mobile'] = None,
            external_order_id: str | None = None,
            payment_method: list[t.Literal[
                'card', 'google_pay', 'apple_pay', 'bog_p2p',
                'bog_loyalty', 'bnpl', 'bog_loan', 'gift_card'
            ]] = 'card',
            ttl: int = 15,
            accept_language: t.Literal['ka', 'en'] = 'ka',
            theme: t.Literal['light', 'dark'] = 'light',
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: tuple[int, int] | int = (3, 10)
    ) -> CheckoutPaymentResponse | ErrorResponse:
        """
        recurring payment api docs: https://api.bog.ge/docs/payments/saved-card/recurrent-payment

        :param parent_order_id: The order identifier
        :param basket: The purchase information.
        :param total_amount: The full amount is to be paid.
        :param callback_url: The web address of the business (must be HTTPS),
                            which will be automatically called by the bank upon
                            completion of the payment to provide the business
                            with the payment details (via Callback).
        :param total_discount_amount: The reduced amount in case of payment with
                                      a discount.
        :param currency:
        :param delivery_amount: Information about the delivery service.
        :param buyer: Information about the buyer.
        :param config: Configuration of a specific payment.
        :param capture: Payment method for pre-authorization or immediate payment.
        :param redirect_urls: The business web addresses that customers can be
                              redirected to from the online payment system upon
                              completion of the payment.
        :param application_type: Defines the type of application from which the
                                 order was created.
        :param external_order_id: The payment identifier from the business system
                                 (e.g., the purchase basket identifier).
        :param payment_method: The payment methods that a customer can use to
                               pay for the order. The business must have all the
                               methods it provides here activated.
        :param ttl: Specifies the duration of the order lifespan in minutes.
        :param accept_language: The language of the interface that the customer
                                will see when redirected to the online payment page.
        :param theme: The theme of the interface that the customer will see when
                      redirected to the online payment page.
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :param verify: in which case it controls whether we verify
                       the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
                        before giving up
        :type timeout: int or Tuple[int, int]

        :return: CheckoutPaymentResponse
        """
        callback_url = callback_url or self.config.callback_url
        if not callback_url:
            raise ValueError('The `callback_url` parameter is required.')
        if redirect_urls:
            redirect_urls = RedirectUrls(**redirect_urls)
        else:
            redirect_urls = RedirectUrls(
                fail=self.config.redirect_urls.fail,
                success=self.config.redirect_urls.success,
            )
            if redirect_urls is None:
                raise ValueError('The `redirect_urls` parameter is required.')
        delivery = None
        if delivery_amount:
            delivery = Delivery(amount=delivery_amount)
        purchase_units = OrderPurchaseUnits(
            total_amount=total_amount,
            basket=basket,
            total_discount_amount=total_discount_amount,
            currency=currency,
            delivery=delivery
        )
        data = to_dict(OrderCheckoutData(
            purchase_units=purchase_units,
            application_type=application_type,
            buyer=buyer,
            config=config,
            capture=capture,
            redirect_urls=redirect_urls,
            callback_url=callback_url,
            external_order_id=external_order_id,
            ttl=ttl,
            payment_method=payment_method,
        ), dropna=True)
        request = Request(
            'POST',
            self.recurrent_payment_api.format(parent_order_id=parent_order_id),
            json=data,
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        if accept_language:
            request.headers['Accept-Language'] = accept_language
        if theme:
            request.headers['Theme'] = theme
        response = request.send()
        self._set_original_response(self.checkout, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return CheckoutPaymentResponse(**response.json())

    def subscribe_payment(
            self,
            *,
            parent_order_id: str,
            callback_url: str | None = None,
            external_order_id: str | None = None,
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: tuple[int, int] | int = (3, 10)
    ) -> CheckoutPaymentResponse | ErrorResponse:
        """
        subscribe payment api docs: https://api.bog.ge/docs/payments/saved-card/offline-payment

        :param parent_order_id: The order identifier
        :param callback_url: The web address of the business (must be HTTPS),
                            which will be automatically called by the bank upon
                            completion of the payment to provide the business
                            with the payment details (via Callback).
        :param external_order_id: The payment identifier from the business system
                                 (e.g., the purchase basket identifier).
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :param verify: in which case it controls whether we verify
                       the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
                        before giving up
        :type timeout: int or Tuple[int, int]

        :return: CheckoutPaymentResponse
        """
        callback_url = callback_url or self.config.callback_url
        if not callback_url:
            raise ValueError('The `callback_url` parameter is required.')
        request = Request(
            'POST',
            self.subscribe_payment_api.format(parent_order_id=parent_order_id),
            json=to_dict(SubscribePaymentData(
                callback_url=callback_url,
                external_order_id=external_order_id,
            ), dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        response = request.send()
        self._set_original_response(self.checkout, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return CheckoutPaymentResponse(**response.json())

    def pre_auth_approve(
            self,
            *,
            order_id: str,
            amount: Decimal | float | int  | None = None,
            description: str | None = None,
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> BogPreAuthResponse | ErrorResponse:
        """
        :param order_id: The order identifier for recurring payment
        :param amount: The amount of the payment
        :param description: The description of the payment approve
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        """
        request = Request(
            'POST',
            self.pre_auth_approve_api.format(order_id=order_id),
            json=to_dict(PreAuthPaymentData(
                amount=amount,
                description=description,
            ), dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return BogPreAuthResponse(**response.json())

    def pre_auth_reject(
            self,
            *,
            order_id: str,
            description: str | None = None,
            idempotency_key: uuid.UUID | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> BogPreAuthResponse | ErrorResponse:
        """
        :param order_id: The order identifier for recurring payment
        :param description: The description of the payment decline
        :param idempotency_key: The Idempotency-Key parameter should be unique
                    for each new API request. This functionality is particularly
                    useful to ensure consistent outcome in scenarios where network
                    issues or retries may lead to duplicate requests.
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        """
        request = Request(
            'POST',
            self.pre_auth_reject_api.format(order_id=order_id),
            json=to_dict(PreAuthPaymentData(
                description=description,
            ), dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        idempotency_key = idempotency_key or self.idempotency_key
        request.headers['Idempotency-Key'] = str(idempotency_key)
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return BogPreAuthResponse(**response.json())

    def refund(
            self,
            *,
            order_id: str,
            amount: Decimal | None = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> BogRefundResponse | ErrorResponse:
        """
        refund api docs: https://api.bog.ge/docs/payments/refund

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
            'GET',
            self.refund_api.format(order_id=order_id),
            json=to_dict(OrderRefundData(amount=amount), dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.order_payment_details, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return BogRefundResponse(**response.json())


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
            data=to_dict(AuthData()),
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
        data = to_dict(
            CheckoutData(
                amount=amount,
                items=items,
                currency_code=currency_code,
                intent=intent,
                capture_method=capture_method,
                locale=locale,
                redirect_url=redirect_url,
                show_shop_order_id_on_extract=show_shop_order_id_on_extract,
            ),
            dropna=True
        )
        request = Request(
            'POST',
            self.checkout_api,
            json=data,
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
            json=to_dict(RefundData(
                order_id=order_id,
                amount=amount
            ), dropna=True),
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
            json=to_dict(OrderStatusData(order_id=order_id)),
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
            json=to_dict(OrderData(order_id=order_id)),
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
            json=to_dict(OrderPaymentStatusData(order_id=order_id)),
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
            json=to_dict(PreAuthData(
                order_id=order_id,
                auth_type=auth_type,
                amount=amount,
            ), dropna=True),
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
            json=to_dict(SubscriptionData(
                order_id=order_id,
                amount=amount,
                currency_code=currency_code,
                shop_order_id=shop_order_id,
                purchase_description=purchase_description,
            ), dropna=True),
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

    # Instalments Services

    def installment_checkout(
            self,
            *,
            cart_items: t.List[t.Dict[str, t.Any]],
            shop_order_id: str,
            installment_month: int,
            installment_type: t.Literal['STANDARD', 'ZERO'],
            success_redirect_url: str,
            fail_redirect_url: str,
            reject_redirect_url: str,
            amount: Decimal | float | int | None = None,
            currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL',
            locale: t.Literal['ka', 'en-US'] = 'ka',
            validate_items: bool = False,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> CheckoutResponse | ErrorResponse:
        """
        installment checkout api docs: https://api.bog.ge/docs/installment/create-order

        :param amount: Amount to be paid
        :type amount: Decimal or str or float or int
        :param cart_items: The list of products purchased
        :type cart_items: list of dict
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
        :param success_redirect_url: A success redirection URL for customers after completing
        an online payment.
        :type success_redirect_url: str
        :param fail_redirect_url: A fail redirection URL for customers after completing
        an online payment.
        :type fail_redirect_url: str
        :param reject_redirect_url: A fail redirection URL for customers after completing
        an online payment.
        :type reject_redirect_url: str
        :param validate_items: Defines what kind of payment info
        will be shown to a customer on an Online Payment Webpage.
        :type validate_items: bool
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        :return: CheckoutResponse
        """

        data = to_dict(
            InstallmentCheckoutData(
                installment_month=installment_month,
                installment_type=installment_type,
                shop_order_id=shop_order_id,
                amount=amount,
                cart_items=cart_items,
                currency_code=currency_code,
                locale=locale,
                success_redirect_url=success_redirect_url,
                fail_redirect_url=fail_redirect_url,
                reject_redirect_url=reject_redirect_url,
                validate_items=validate_items,
            ),
            dropna=True
        )
        request = Request(
            'POST',
            self.installment_checkout_api,
            json=data,
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.installment_checkout, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return CheckoutResponse(**response.json())

    def installment_calculate(
            self,
            *,
            amount: Decimal,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int
    ) -> CalculateResponse | ErrorResponse:
        """
        installment calculate api docs: https://api.bog.ge/docs/installment/get-discounts
        :param amount:
        :param verify:
        :param timeout:

        :return:
        """
        request = Request(
            'POST',
            self.installment_calculate_api,
            json=to_dict(InstallmentCalculateData(
                amount=amount,
                client_id=self.config.client_id
            ), dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.installment_calculate, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return CalculateResponse(discounts=response.json())

    def installment_order(
            self,
            *,
            order_id: str,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int
    ) -> InstallmentOrderResponse | ErrorResponse:
        """
        installment order api docs: https://api.bog.ge/docs/installment/installment-details
        :param order_id:
        :param verify:
        :param timeout:

        :return: InstallmentOrderResponse
        """
        request = Request(
            'POST',
            self.installment_order_api,
            json=to_dict(InstallmentOrderData(order_id=order_id), dropna=True),
            headers=self.headers,
            verify=verify,
            timeout=timeout,
            **{'verbose': self.config.verbose}
        )
        response = request.send()
        self._set_original_response(self.installment_order, response)
        if response.status_code != 200:
            return ErrorResponse(response)
        return InstallmentOrderResponse(**response.json())
