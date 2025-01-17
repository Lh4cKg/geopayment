from __future__ import annotations

import typing as t
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_UP

from geopayment.enums import (
    Currency, AuthType, Language, CapturedMethod,
    Intent, PaymentMethod, ApplicationType
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
class InstallmentCartItem(BaseModel):
    total_item_amount: Decimal
    item_description: str
    total_item_qty: int
    item_vendor_code: str
    product_image_url: str | None = None
    item_site_detail_url: str | None = None

    def __post_init__(self):
        if self.total_item_amount:
            self.total_item_amount = Decimal(
                self.total_item_amount
            ).quantize(Decimal('.00'), rounding=ROUND_UP)


@dataclass
class InstallmentCheckoutData(BaseModel):
    cart_items: t.List[InstallmentCartItem | t.Dict[str, t.Any]]
    shop_order_id: str
    success_redirect_url: str
    fail_redirect_url: str
    reject_redirect_url: str
    installment_month: int
    installment_type: t.Literal['STANDARD', 'ZERO'] = 'STANDARD'
    amount: Decimal | None = None
    intent: t.Literal['LOAN'] = 'LOAN'
    locale: t.Literal['ka', 'en-US'] = 'ka'
    currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL'
    purchase_units: t.List[PurchaseUnit | t.Dict[str, t.Any]] = field(default_factory=list)
    validate_items: bool = True

    def __post_init__(self):
        if self.intent != 'LOAN':
            raise ValueError('`intent` must be `AUTHORIZE` or `CAPTURE`')
        try:
            Language(self.locale)
        except ValueError:
            raise ValueError('`locale` must be `ka` or `en-US`')
        if self.currency_code not in Currency.allowed_currencies():
            raise ValueError('The specified `currency_code` is not supported.')
        if self.amount:
            self.amount = Decimal(self.amount).quantize(Decimal('.00'), rounding=ROUND_UP)
        if not isinstance(self.cart_items, list):
            raise ValueError('The `items` must be of type list')

        amount = Decimal(0)
        items = []
        for item in self.cart_items:
            # validate item attributes
            item = InstallmentCartItem(**item)
            amount += item.total_item_amount
            items.append(item)

        self.cart_items = items

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
class InstallmentCalculateData(BaseModel):
    amount: Decimal
    client_id: str

    def __post_init__(self):
        self.amount = Decimal(self.amount).quantize(Decimal('.00'), rounding=ROUND_UP)


@dataclass
class InstallmentOrderData(BaseModel):
    order_id: str


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


###################################
#   BOG New Online Payment API    #
###################################


@dataclass
class Buyer(BaseModel):
    full_name: str
    masked_email: str | None = None
    masked_phone: str | None = None

    def __post_init__(self):
        if self.masked_phone:
            self.masked_phone = f'{self.masked_phone[:2]}*****{self.masked_phone[-2:]}'
        if self.masked_email:
            try:
                username, domain = self.masked_email.split('@')
                mask = '*' * (len(username) - 2)
                self.masked_email = f'{username[:1]}{mask}{username[-1:]}@{domain}'
            except ValueError:
                raise ValueError('The specified `masked_email` is not valid.')


@dataclass
class Basket(BaseModel):
    product_id: str
    quantity: int
    unit_price: Decimal
    unit_discount_price: Decimal | None = None
    vat: Decimal | None = None
    vat_percent: int | float | None = None
    total_price: Decimal | None = None
    image: str | None = None
    package_code: str | None = None
    tin: str | None = None
    pinfl: str | None = None
    product_discount_id: str | None = None
    description: str | None = None

    def __post_init__(self):
        self.unit_price = Decimal(self.unit_price).quantize(Decimal('.00'), ROUND_UP)
        if self.unit_discount_price:
            self.unit_discount_price = Decimal(
                self.unit_discount_price
            ).quantize(Decimal('.00'), ROUND_UP)
        if self.total_price:
            self.total_price = Decimal(
                self.total_price
            ).quantize(Decimal('.00'), ROUND_UP)



@dataclass
class Delivery(BaseModel):
    amount: Decimal | None = None

    def __post_init__(self):
        if self.amount:
            self.amount = Decimal(self.amount).quantize(Decimal('.00'), ROUND_UP)


@dataclass
class OrderPurchaseUnits(BaseModel):
    total_amount: Decimal
    basket: t.List[Basket | t.Dict[str, t.Any]]
    total_discount_amount: Decimal | None = None
    currency: t.Literal['GEL', 'USD', 'EUR', 'GBP'] = 'GEL'
    delivery: Delivery | None = None

    def __post_init__(self):
        baskets = []
        for basket in self.basket:
            if isinstance(basket, dict):
                baskets.append(Basket(**basket))
            else:
                baskets.append(basket)
        self.basket = baskets
        self.total_discount_amount = Decimal(
            self.total_discount_amount
        ).quantize(Decimal('.00'), ROUND_UP)
        if self.currency not in Currency.allowed_currencies():
            raise ValueError('The specified `currency` is not supported.')


@dataclass
class RedirectUrls(BaseModel):
    success: str
    fail: str


@dataclass
class Loan(BaseModel):
    type: str
    month: int


@dataclass
class Campaign(BaseModel):
    card: t.Literal['visa', 'ms', 'solo']
    type: t.Literal['restrict', 'client_discount']


@dataclass
class GooglePay(BaseModel):
    google_pay_token: str
    external: bool = False


@dataclass
class ApplePay(BaseModel):
    external: bool = False


@dataclass
class Account(BaseModel):
    tag: str


@dataclass
class Config(BaseModel):
    loan: Loan | None = None
    campaign: Campaign | None = None
    google_pay: GooglePay | None = None
    apple_pay: ApplePay | None = None
    account: Account | None = None


@dataclass
class OrderCheckoutData(BaseModel):
    callback_url: str
    purchase_units: OrderPurchaseUnits
    application_type: t.Literal['web', 'mobile'] | None = None
    buyer: Buyer | None = None
    redirect_urls: RedirectUrls | None = None
    external_order_id: str | None = None
    capture: t.Literal['automatic', 'manual'] = 'automatic'
    ttl: int = 1440
    payment_method: t.List[t.Literal[
        'card', 'google_pay', 'apple_pay', 'bog_p2p',
        'bog_loyalty', 'bnpl', 'bog_loan', 'gift_card'
    ]] = 'card'
    config: Config | None = None

    def __post_init__(self):
        try:
            ApplicationType(self.application_type)
        except ValueError:
            values = ' or '.join([
                f'`{v._value_}`' for _,v in ApplicationType._member_map_.items()
            ])
            raise ValueError(
                f'`application_type` must be {values}'
            )
        try:
            PaymentMethod(self.payment_method)
        except ValueError:
            values = ' or '.join([
                f'`{v._value_}`' for _,v in PaymentMethod._member_map_.items()
            ])
            raise ValueError(
                f'`payment_method` must be {values}'
            )
