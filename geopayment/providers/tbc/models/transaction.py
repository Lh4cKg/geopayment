import typing as t

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    create: str = 'v'
    status: str = 'c'
    reversal: str = 'r'
    refund: str = 'k'
    pre_auth: str = 'a'
    pre_auth_confirm: str = 't'
    pre_auth_card_register_confirm: str = 'd'
    card_register: str = 'p'
    card_register_confirm: str = 'z'
    recurring: str = 'e'
    pre_auth_recurring: str = 'f'
    refund_to_debit_card: str = 'g'
    end_business_day: str = 'b'


@dataclass(frozen=True)
class MessageType:
    sms: t.Literal['SMS'] = 'SMS'
    dms: t.Literal['DMS'] = 'DMS'
    auth: t.Literal['AUTH'] = 'AUTH'
