from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from geopayment.providers.bog.models.base import BaseModel
from geopayment.providers.bog.models.request import Amount


@dataclass
class SuccessResponse(BaseModel):
    status_code: int
    text: str | None = None
    success: str = 'Ok'


@dataclass
class ErrorResponseResult(BaseModel):
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
class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    app_id: str | None = None
    scope: str | None = None
    refresh_expires_in: int | None = None
    not_before_policy: int | None = None
    status_code: int | None = None


@dataclass
class CheckoutLink(BaseModel):
    href: str
    rel: str
    method: str


@dataclass
class CheckoutResponse(BaseModel):
    status: str
    payment_hash: str
    order_id: str
    links: t.List[CheckoutLink | t.Dict[str, str]] = field(default_factory=list)
    rel_approve: str | None = None

    def __post_init__(self):
        links = []
        for link in self.links:
            link = CheckoutLink(**link)
            if link.rel == 'approve':
                self.rel_approve = link.rel
            links.append(link)


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
    captures: t.List[Capture] = field(default_factory=list)

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
    payments: t.List[Payment] = field(default_factory=list)
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
class OrderResponse(BaseModel):
    id: str
    status: str
    intent: str
    purchaseUnit: PurchaseUnit
    payer: Payer
    createTime: str | None = None
    updateTime: str | None = None
    errorHistory: t.List = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.purchaseUnit, dict):
            self.purchaseUnit = PurchaseUnit(**self.purchaseUnit)
        if isinstance(self.payer, dict):
            self.payer = Payer(**self.payer)


@dataclass
class OrderStatusResponse(BaseModel):
    status: str


@dataclass
class OrderPaymentResponse(BaseModel):
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
class PreAuthResponse(BaseModel):
    status: t.Literal['success', 'error', 'in_progress']
    description: str


@dataclass
class SubscriptionResponse(BaseModel):
    status: t.Literal['success', 'error', 'in_progress']
    payment_hash: str
    order_id: str
