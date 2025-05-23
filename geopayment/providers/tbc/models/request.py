from __future__ import annotations

import typing as t

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Create:
    command: str
    amount: int
    currency: int
    client_ip_addr: str
    description: str
    language: t.Literal['ka', 'en'] = 'ka'


@dataclass
class Status:
    command: str
    trans_id: str
    client_ip_addr: str


@dataclass
class Reversal:
    command: str
    trans_id: str
    amount: int


@dataclass
class Refund(Reversal):
    pass


@dataclass
class RefundToDebitCard(Reversal):
    pass


@dataclass
class PreAuth:
    command: str
    amount: int
    currency: int
    description: str
    client_ip_addr: str
    msg_type: t.Literal['SMS', 'DMS', 'AUTH']
    language: t.Literal['ka', 'en'] = 'ka'


@dataclass
class PreAuthConfirm:
    command: str
    trans_id: str
    amount: int
    currency: int
    description: str
    client_ip_addr: str
    msg_type: t.Literal['SMS', 'DMS', 'AUTH']
    language: t.Literal['ka', 'en'] = 'ka'


@dataclass
class CardRegisterConfirm:
    command: str
    amount: int
    currency: int
    description: str
    client_ip_addr: str
    msg_type: t.Literal['SMS', 'DMS', 'AUTH']
    biller_client_id: str
    expiry: str = Field(min_length=4, max_length=4, pattern=r'^(0[1-9]|1[0-2])\d{2}$')
    perspayee_expiry: str
    perspayee_gen: str
    language: t.Literal['ka', 'en'] = 'ka'


@dataclass
class PreAuthCardRegisterConfirm(CardRegisterConfirm):
    pass


@dataclass
class CardRegister:
    command: str
    currency: int
    description: str
    client_ip_addr: str
    msg_type: t.Literal['SMS', 'DMS', 'AUTH']
    biller_client_id: str
    expiry: str = Field(min_length=4, max_length=4, pattern=r'^(0[1-9]|1[0-2])\d{2}$')
    perspayee_expiry: str
    perspayee_gen: str
    language: t.Literal['ka', 'en'] = 'ka'


@dataclass
class Recurring:
    command: str
    amount: int
    currency: int
    description: str
    client_ip_addr: str
    biller_client_id: str
    language: t.Literal['ka', 'en'] = 'ka'


@dataclass
class PreAuthRecurring(Recurring):
    pass


@dataclass
class EndOfBusinessDay:
    command: str
