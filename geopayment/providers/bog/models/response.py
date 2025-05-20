from __future__ import annotations

import typing as t
import uuid
from pydantic import Field
from pydantic.dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from geopayment.providers.bog.models.request import Amount


@dataclass
class SuccessResponse:
    status_code: int
    text: str | None = None
    success: str = 'Ok'


@dataclass
class ErrorResponseResult:
    error_code: int
    error_message: str
    information_link: str | None = None
    details: str | None = None
    http_status_code: int | None = None


class ErrorResponse:

    def __new__(cls, *args, **kwargs) -> ErrorResponseResult:
        response = args[0]
        try:
            return ErrorResponseResult(
                **response.json(),
                http_status_code=response.status_code
            )
        except Exception:
            return ErrorResponseResult(
                error_code=response.status_code,
                error_message=response.text,
                http_status_code=response.status_code
            )

    def __init__(self, response) -> None:
        self.response = response


@dataclass
class AuthResponse:
    access_token: str
    token_type: str
    expires_in: int
    app_id: str | None = None
    scope: str | None = None
    refresh_expires_in: int | None = None
    not_before_policy: int | None = None
    status_code: int | None = None


@dataclass
class CheckoutLink:
    href: str
    rel: str
    method: str


@dataclass
class CheckoutResponse:
    status: str
    payment_hash: str
    order_id: str
    links: t.List[CheckoutLink | t.Dict[str, str]] = Field(default_factory=list)
    rel_approve: str | None = None

    def __post_init__(self):
        links = []
        for link in self.links:
            link = CheckoutLink(**link)
            if link.rel == 'approve':
                self.rel_approve = link.rel
            links.append(link)
        self.links = links


@dataclass
class RefundResponse(SuccessResponse):
    pass


@dataclass
class Payer:
    name: str | None = None
    email_address: str | None = None
    payer_id: str | None = None


@dataclass
class Payee:
    addres: str
    email_address: str
    contact: str


@dataclass
class Capture:
    id: str
    status: str
    amount: Amount
    final_capture: bool
    create_time: str
    update_time: str

    def __post_init__(self):
        if isinstance(self.amount, dict):
            self.amount = Amount(**self.amount)


@dataclass
class Payment:
    captures: t.List[Capture] = Field(default_factory=list)

    def __post_init__(self):
        captures = []
        for capture in self.captures:
            if isinstance(capture, dict):
                captures.append(Capture(**capture))
            else:
                captures.append(capture)
        self.captures = captures


@dataclass
class PurchaseUnit:
    amount: Amount
    payee: Payee
    payments: t.List[Payment] = Field(default_factory=list)
    shop_order_id: str | None = None

    def __post_init__(self):
        if isinstance(self.amount, dict):
            self.amount = Amount(**self.amount)
        if isinstance(self.payee, dict):
            self.payee = Payee(**self.payee)
        payments = []
        for payment in self.payments:
            if isinstance(payment, dict):
                payments.append(Payment(**payment))
            else:
                payments.append(payment)
        self.payments = payments


@dataclass
class OrderResponse:
    id: str
    status: str
    intent: str
    purchaseUnit: PurchaseUnit
    payer: Payer
    createTime: str | None = None
    updateTime: str | None = None
    errorHistory: t.List = Field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.purchaseUnit, dict):
            self.purchaseUnit = PurchaseUnit(**self.purchaseUnit)
        if isinstance(self.payer, dict):
            self.payer = Payer(**self.payer)


@dataclass
class OrderStatusResponse:
    status: str


@dataclass
class OrderPaymentResponse:
    status: t.Literal['success', 'error', 'in_progress']
    order_id: str
    payment_hash: str
    ipay_payment_id: str
    status_description: str
    shop_order_id: str
    payment_method: str
    card_type: str
    pan: str | None = None
    transaction_id: str | None = None
    pre_auth_status: str | None = None


@dataclass
class PreAuthResponse:
    status: t.Literal['success', 'error', 'in_progress']
    description: str


@dataclass
class SubscriptionResponse:
    status: t.Literal['success', 'error', 'in_progress']
    payment_hash: str
    order_id: str


@dataclass
class CalculateDiscount:
    month: int
    amount: str | Decimal
    discount_code: t.Literal['ZERO', 'STANDARD']


@dataclass
class CalculateResponse:
    discounts: t.List[CalculateDiscount | t.Dict[str, t.Any]]

    def __post_init__(self):
        discounts = []
        for discount in self.discounts:
            discounts.append(CalculateDiscount(**discount))
        self.discounts = discounts


@dataclass
class InstallmentOrderResponse:
    order_id: str
    status: t.Literal['success', 'error', 'in_progress']
    installment_status: t.Literal['success', 'reject', 'reverse_success', 'fail', 'unknown']
    ipay_payment_id: str
    shop_order_id: str
    payment_method: str


# Bog API

@dataclass
class _Links:
    details: dict[str, t.Any]
    redirect: dict[str, t.Any]


@dataclass
class OrderCheckoutResponse:
    id: str
    _links: _Links | dict[str, t.Any]
    details: str | None = None
    redirect: str | None = None

    def __post_init__(self):
        if isinstance(self._links, dict):
            self._links = _Links(**self._links)
        self.details = self._links.details['href']
        self.redirect = self._links.redirect['href']


@dataclass
class OrderPaymentClient:
    id: str
    brand_ka: str
    brand_en: str
    url: str

@dataclass
class OrderPaymentStatus:
    key: t.Literal[
        'created', 'processing', 'completed', 'rejected', 'refund_requested',
        'refunded', 'refunded_partially', 'auth_requested', 'blocked',
        'partial_completed'
    ]
    value: str


@dataclass
class OrderPaymentBuyer:
    full_name: str
    email: str
    phone_number: str


@dataclass
class OrderPaymentPurchaseItem:
    external_item_id: str
    description: str
    quantity: int
    unit_price: Decimal
    unit_discount_price: Decimal
    vat: Decimal
    vat_percent: Decimal
    total_price: Decimal
    package_code: str
    tin: str | None = None
    pinfl: str | None = None
    product_discount_id: str | None = None


@dataclass
class OrderPaymentPurchaseUnit:
    request_amount: Decimal
    transfer_amount: Decimal
    refund_amount: Decimal
    currency_code: t.Literal['GEL', 'USD', 'EUR']
    items: list[OrderPaymentPurchaseItem]


@dataclass
class OrderPaymentRedirectLinks:
    fail: str
    success: str


@dataclass
class OrderPaymentTransferMethod:
    key: t.Literal['card', 'google_pay', 'apple_pay', 'bog_p2p', 'bog_loyalty', 'bnpl', 'bog_loan']
    value: str


@dataclass
class OrderPaymentDetail:
    transfer_method: OrderPaymentTransferMethod
    code: str
    code_description: str
    transaction_id: str
    payer_identifier: str
    payment_option: t.Literal['direct_debit', 'recurrent', 'subscription']
    card_type: t.Literal['amex', 'mc', 'visa']
    card_expiry_date: str
    request_account_tag: str
    transfer_account_tag: str
    saved_card_type: t.Literal['recurrent', 'subscription']
    parent_order_id: str


@dataclass
class OrderPaymentDiscount:
    bank_discount_amount: Decimal
    bank_discount_desc: str
    discounted_amount: Decimal
    original_order_amount: Decimal
    system_discount_amount: Decimal
    system_discount_desc: str


@dataclass
class OrderPaymentAction:
    action_id: str
    request_channel: t.Literal['public_api', 'business_manager', 'support']
    action: t.Literal['authorize', 'partial_authorize', 'cancel_authorize', 'refund', 'partial_refund']
    status: t.Literal['completed', 'rejected']
    zoned_action_date: str
    amount: Decimal


@dataclass
class OrderPaymentDetailsResponse:
    order_id: uuid.UUID | str
    industry: str
    capture: t.Literal['manual', 'automatic']
    external_order_id: str
    client: OrderPaymentClient
    zoned_create_date: datetime
    zoned_expire_date: datetime
    order_status: OrderPaymentStatus
    buyer: OrderPaymentBuyer
    purchase_units: OrderPaymentPurchaseUnit
    redirect_links: OrderPaymentRedirectLinks
    payment_detail: OrderPaymentDetail
    discount: OrderPaymentDiscount
    actions: list[OrderPaymentAction]
    lang: t.Literal['ka', 'en']
    reject_reason: str | None


@dataclass
class BogRefundResponse:
    key: str
    message: str
    action_id: str


@dataclass
class BogPreAuthResponse(BogRefundResponse):
    pass


@dataclass
class RecurrentResponse:
    http_status: int
    message: str | None = None


@dataclass
class Link:
    href: str

@dataclass
class CheckoutPaymentLinks:
    details: Link | dict
    redirect: Link | dict

    def __post_init__(self):
        self.details = Link(**self.details)


@dataclass
class CheckoutPaymentResponse:
    id: str
    _links: CheckoutPaymentLinks | dict
    details: str | None = None
    redirect: str | None = None

    def __post_init__(self):
        self._links = CheckoutPaymentLinks(**self._links)
        self.details = self._links.details.href
        self.redirect = self._links.redirect.href
