import typing as t
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_UP

from geopayment.providers.models import ValidationModel


@dataclass
class AuthData(ValidationModel):
    grant_type: t.Literal['client_credentials'] = 'client_credentials'

    def __post_init__(self):
        if self.grant_type != 'client_credentials':
            raise ValueError('`grant_type` must be `client_credentials`')


@dataclass
class Item(ValidationModel):
    amount: Decimal
    description: str
    quantity: int
    product_id: str


@dataclass
class Amount(ValidationModel):
    value: Decimal
    currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP']


@dataclass
class PurchaseUnit(ValidationModel):
    amount: Amount | dict[str, t.Any]
    # removed from bog apis
    industry_type: t.Literal['ECOMMERCE'] = 'ECOMMERCE'


@dataclass
class CheckoutData(ValidationModel):
    redirect_url: str
    amount: Decimal | None = None
    items: list[Item | dict[str, t.Any]] = field(default_factory=list)
    intent: t.Literal['AUTHORIZE', 'CAPTURE'] = 'AUTHORIZE'
    locale: t.Literal['ka', 'en-US'] = 'ka'
    shop_order_id: str | None = None
    currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL'
    purchase_units: list[PurchaseUnit | dict[str, t.Any]] = field(default_factory=list)
    capture_method: t.Literal['AUTOMATIC', 'MANUAL'] = 'AUTOMATIC'
    show_shop_order_id_on_extract: bool = False

    def __post_init__(self):
        super().__post_init__()
        amount = Decimal(0)
        for item in self.items:
            amount += item.amount

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
class InstallmentCartItem(ValidationModel):
    total_item_amount: Decimal
    item_description: str
    total_item_qty: int
    item_vendor_code: str
    product_image_url: str | None = None
    item_site_detail_url: str | None = None


@dataclass
class InstallmentCheckoutData(ValidationModel):
    cart_items: list[InstallmentCartItem | dict[str, t.Any]]
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
    purchase_units: list[PurchaseUnit | dict[str, t.Any]] = field(default_factory=list)
    validate_items: bool = True

    def __post_init__(self):
        super().__post_init__()

        amount = Decimal(0)
        for item in self.cart_items:
            amount += item.total_item_amount

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
class InstallmentCalculateData(ValidationModel):
    amount: Decimal
    client_id: str


@dataclass
class InstallmentOrderData(ValidationModel):
    order_id: str


@dataclass
class RefundData(ValidationModel):
    order_id: str
    amount: Decimal | None = None


@dataclass
class OrderData(ValidationModel):
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
    currency_code: t.Literal['GEL', 'USD', 'EUR', 'GBP'] = 'GEL'
    shop_order_id: str | None = None
    purchase_description: str | None = None


###################################
#   BOG New Online Payment API    #
###################################


@dataclass
class Buyer(ValidationModel):
    full_name: str
    masked_email: str | None = None
    masked_phone: str | None = None

    def __post_init__(self):
        super().__post_init__()
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
class Basket(ValidationModel):
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
class Delivery(ValidationModel):
    amount: Decimal


@dataclass
class OrderPurchaseUnits(ValidationModel):
    total_amount: Decimal
    basket: list[Basket | dict[str, t.Any]]
    total_discount_amount: Decimal | None = None
    currency: t.Literal['GEL', 'USD', 'EUR', 'GBP'] = 'GEL'
    delivery: Delivery | None = None


@dataclass
class RedirectUrls(ValidationModel):
    success: str
    fail: str


@dataclass
class Loan(ValidationModel):
    type: str
    month: int


@dataclass
class Campaign(ValidationModel):
    card: t.Literal['visa', 'ms', 'solo']
    type: t.Literal['restrict', 'client_discount']


@dataclass
class GooglePay(ValidationModel):
    google_pay_token: str
    external: bool = False


@dataclass
class ApplePay(ValidationModel):
    external: bool = False


@dataclass
class Account(ValidationModel):
    tag: str


@dataclass
class Config(ValidationModel):
    loan: Loan | None = None
    campaign: Campaign | None = None
    google_pay: GooglePay | None = None
    apple_pay: ApplePay | None = None
    account: Account | None = None


@dataclass
class OrderCheckoutData(ValidationModel):
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
class OrderRefundData(ValidationModel):
    amount: Decimal | None
