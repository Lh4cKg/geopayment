from __future__ import annotations

import typing as t
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_UP

from geopayment.enums import (
    Currency, AuthType, Language, CapturedMethod,
    Intent
)
from geopayment.providers.bog.models.base import BaseModel


@dataclass
class AuthData(BaseModel):
    grant_type: t.Literal['client_credentials'] = 'client_credentials'

    def __post_init__(self):
        if self.grant_type != 'client_credentials':
            raise ValueError('`grant_type` must be `client_credentials`')


@dataclass
class Item(BaseModel):
    amount: Decimal
    description: str
    quantity: int
    product_id: str

    def __post_init__(self):
        self.amount = Decimal(self.amount).quantize(
            Decimal('.00'), rounding=ROUND_UP
        )
        if not isinstance(self.description, str):
            raise ValueError(
                f"The `description` must be of type str"
            )
        if not isinstance(self.quantity, int):
            raise ValueError(
                f"The `quantity` must be of type integer"
            )
        if not isinstance(self.product_id, str):
            raise ValueError(
                f"The `product_id` must be of type integer or string"
            )


@dataclass
class Amount(BaseModel):
    value: Decimal
    currency_code: str

    def __post_init__(self):
        self.value = Decimal(self.value).quantize(
            Decimal('.00'), rounding=ROUND_UP
        )


@dataclass
class PurchaseUnit(BaseModel):
    amount: Amount | t.Dict[str, t.Any]
    # removed from bog apis
    industry_type: t.Literal['ECOMMERCE'] = 'ECOMMERCE'

    def __post_init__(self):
        if isinstance(self.amount, dict):
            self.amount = Amount(**self.amount)


@dataclass
class CheckoutData(BaseModel):
    redirect_url: str
    amount: Decimal | None = None
    items: t.List[Item | t.Dict[str, t.Any]] = field(default_factory=list)
    intent: t.Literal['AUTHORIZE', 'CAPTURE'] = 'AUTHORIZE'
    locale: t.Literal['ka', 'en-US'] = 'ka'
    shop_order_id: str | None = None
    currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL'
    purchase_units: t.List[PurchaseUnit | t.Dict[str, t.Any]] = field(default_factory=list)
    capture_method: t.Literal['AUTOMATIC', 'MANUAL'] = 'AUTOMATIC'
    show_shop_order_id_on_extract: bool = False

    def __post_init__(self):
        try:
            Intent(self.intent)
        except ValueError:
            raise ValueError('`intent` must be `AUTHORIZE` or `CAPTURE`')
        try:
            CapturedMethod(self.capture_method)
        except ValueError:
            raise ValueError('`capture_method` must be `AUTOMATIC` or `MANUAL`')
        try:
            Language(self.locale)
        except ValueError:
            raise ValueError('`locale` must be `ka` or `en-US`')
        if self.currency_code not in Currency.allowed_currencies():
            raise ValueError('The specified `currency_code` is not supported.')
        if self.amount:
            self.amount = Decimal(self.amount)
        if not isinstance(self.items, list):
            raise ValueError('The `items` must be of type list')
        if not self.amount and not self.items:
            raise ValueError('Either `amount` or `items` must be specified.')

        amount = Decimal(0)
        items = []
        for item in self.items:
            # validate item attributes
            item = Item(**item)
            amount += item.amount
            items.append(item)

        if items:
            self.items = items

        amount = self.amount or amount
        self.purchase_units.append(
            PurchaseUnit(
                amount={
                    'currency_code': self.currency_code,
                    'value': amount.quantize(
                        Decimal('.00'), rounding=ROUND_UP
                    )
                }
            )
        )
        self.currency_code = None
        self.amount = None


@dataclass
class RefundData(BaseModel):
    order_id: str
    amount: Decimal | None = None

    def __post_init__(self):
        if self.amount:
            self.amount = Decimal(self.amount).quantize(Decimal('.00'), ROUND_UP)


@dataclass
class OrderData(BaseModel):
    order_id: str


@dataclass
class OrderStatusData(OrderData):
    pass


@dataclass
class OrderPaymentStatusData(OrderData):
    pass


@dataclass
class PreAuthData(OrderData):
    auth_type: t.Literal['FULL_COMPLETE', 'PARTIAL_COMPLETE', 'CANCEL']
    amount: Decimal | None = None

    def __post_init__(self):
        if self.amount:
            self.amount = Decimal(self.amount).quantize(Decimal('.00'), ROUND_UP)
        try:
            AuthType(self.auth_type)
        except ValueError:
            raise ValueError('The specified `auth_type` is not supported.')


@dataclass
class SubscriptionData(OrderData):
    order_id: str
    amount: Decimal
    currency_code: t.Literal['GEL', 'USD', 'EUR', 'GBP'] = 'GEL'
    shop_order_id: str | None = None
    purchase_description: str | None = None

    def __post_init__(self):
        self.amount = Decimal(self.amount).quantize(Decimal('.00'), ROUND_UP)
        if self.currency_code not in Currency.allowed_currencies():
            raise ValueError('The specified `currency_code` is not supported.')
