import typing as t
from decimal import Decimal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class AuthData:
    grant_type: t.Literal['client_credentials'] = 'client_credentials'


@dataclass
class Item:
    amount: Decimal
    description: str
    quantity: int
    product_id: str


@dataclass
class Amount:
    value: Decimal
    currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP']


@dataclass
class PurchaseUnit:
    amount: Amount | dict
    # removed from bog apis
    industry_type: t.Literal['ECOMMERCE'] = 'ECOMMERCE'


@dataclass
class CheckoutData:
    redirect_url: str
    amount: Decimal | None = None
    shop_order_id: str | None = None
    items: list[Item | dict[str, t.Any]] = Field(default_factory=list)
    intent: t.Literal['AUTHORIZE', 'CAPTURE'] = 'AUTHORIZE'
    locale: t.Literal['ka', 'en-US'] = 'ka'
    currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL'
    purchase_units: list[PurchaseUnit] = Field(default_factory=list)
    capture_method: t.Literal['AUTOMATIC', 'MANUAL'] = 'AUTOMATIC'
    show_shop_order_id_on_extract: bool = False

    def __post_init__(self):
        amount = Decimal(0)
        for item in self.items:
            amount += item.amount

        amount = self.amount or amount
        self.purchase_units.append(
            PurchaseUnit(
                amount={
                    'currency_code': self.currency_code,
                    'value': amount
                }
            )
        )
        self.currency_code = None
        self.amount = None


@dataclass
class RefundData:
    order_id: str
    amount: Decimal | None = None


@dataclass
class OrderData:
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


@dataclass
class SubscriptionData(OrderData):
    order_id: str
    amount: Decimal
    shop_order_id: str | None = None
    purchase_description: str | None = None
    currency_code: t.Literal['GEL', 'USD', 'EUR', 'GBP'] = 'GEL'


###################################
#   BOG New Online Payment API    #
###################################


@dataclass
class Buyer:
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
class Basket:
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


@dataclass
class Delivery:
    amount: Decimal


@dataclass
class OrderPurchaseUnits:
    total_amount: Decimal
    basket: list[Basket] #  | dict[str, t.Any]
    total_discount_amount: Decimal | None = None
    delivery: Delivery | None = None
    currency: t.Literal['GEL', 'USD', 'EUR', 'GBP'] = 'GEL'


@dataclass
class RedirectUrls:
    success: str
    fail: str


@dataclass
class Loan:
    type: str
    month: int


@dataclass
class Campaign:
    card: t.Literal['visa', 'ms', 'solo']
    type: t.Literal['restrict', 'client_discount']


@dataclass
class GooglePay:
    google_pay_token: str
    external: bool = False


@dataclass
class ApplePay:
    external: bool = False


@dataclass
class Account:
    tag: str


@dataclass
class Config:
    loan: Loan | None = None
    campaign: Campaign | None = None
    google_pay: GooglePay | None = None
    apple_pay: ApplePay | None = None
    account: Account | None = None


@dataclass
class OrderCheckoutData:
    callback_url: str
    purchase_units: OrderPurchaseUnits
    application_type: t.Literal['web', 'mobile'] | None = None
    buyer: Buyer | dict[str, str] | None = None
    redirect_urls: RedirectUrls | dict[str, str] | None = None
    external_order_id: str | None = None
    capture: t.Literal['automatic', 'manual'] = 'automatic'
    ttl: int = 15
    payment_method: list[t.Literal[
        'card', 'google_pay', 'apple_pay', 'bog_p2p',
        'bog_loyalty', 'bnpl', 'bog_loan', 'gift_card'
    ]] = 'card'
    config: Config | dict[str, t.Any] | None = None


@dataclass
class OrderRefundData:
    amount: Decimal | None = None


@dataclass
class SubscribePaymentData:
    callback_url: str | None = None
    external_order_id: str | None = None


@dataclass
class PreAuthPaymentData:
    amount: Decimal | None = None
    description: str | None = None
