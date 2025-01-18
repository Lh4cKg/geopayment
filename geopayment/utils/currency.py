from __future__ import annotations

import typing as t
from decimal import Decimal

from geopayment.enums import Currency


def gel_to_tetri(
        amount: t.Union[int, float, Decimal],
        quantize: str = '1.00') -> int:
    """

    :param amount: type of decimal
    :param quantize: type of string
    :return: amount in tetri

    >>> amount = Decimal('0.01')
    >>> gel_to_tetri(amount)
    1
    """
    return int(Decimal(amount).quantize(Decimal(quantize)) * 100)


def get_currency_code(code: str | int) -> int:
    """

    :param code: currency code or currency symbol
    :type code: str | int
    :return: currency code
    """

    try:
        Currency(code)
        return code
    except ValueError:
        pass

    allowed_currencies = Currency.allowed_currencies()
    if code not in allowed_currencies:
        raise ValueError('The Specified currency `code` is not allowed')

    return allowed_currencies[code].value
