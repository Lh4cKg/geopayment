import typing as t
from decimal import Decimal

from pydantic import Field
from pydantic.dataclasses import dataclass

from geopayment.providers.bog.models.request import PurchaseUnit


@dataclass
class InstallmentCartItem:
    total_item_amount: Decimal
    item_description: str
    total_item_qty: int
    item_vendor_code: str
    product_image_url: str | None = None
    item_site_detail_url: str | None = None


@dataclass
class InstallmentCheckoutData:
    cart_items: list[InstallmentCartItem]
    shop_order_id: str
    success_redirect_url: str
    fail_redirect_url: str
    reject_redirect_url: str
    installment_month: int
    amount: Decimal | None = None
    installment_type: t.Literal['STANDARD', 'ZERO'] = 'STANDARD'
    intent: t.Literal['LOAN'] = 'LOAN'
    locale: t.Literal['ka', 'en-US'] = 'ka'
    currency_code: t.Literal['GEL', 'EUR', 'USD', 'GBP'] = 'GEL'
    purchase_units: list[PurchaseUnit] = Field(default_factory=list)
    validate_items: bool = True

    def __post_init__(self):
        amount = Decimal(0)
        for item in self.cart_items:
            amount += item.total_item_amount

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
class InstallmentCalculateData:
    amount: Decimal
    client_id: str


@dataclass
class InstallmentOrderData:
    order_id: str

