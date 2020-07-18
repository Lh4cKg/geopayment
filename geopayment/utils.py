# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

from decimal import Decimal
from functools import wraps
import requests

from .constants import (
    CURRENCY_CODES,
    CURRENCY_SYMBOLS,
    ALLOW_CURRENCY_CODES
)


def get_client_ip(request):
    """
    This method support only Django web framework
    :param request:
    :return: client ip address
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_response(content):
    """

    :param content: response from payment provider
    :return: dict

    >>> parse_response('TRANSACTION_ID: Du1eT2N1M4defU743iOpF6G8OYt')
    {'TRANSACTION_ID': 'Du1eT2N1M4defU743iOpF6G8OYt='}
    """

    return dict(
        item.split(': ')
        for item in content.split('\n')
        if item.strip()
    )


def gel_to_tetri(amount):
    """

    :param amount: type of decimal
    :return: amount in tetri

    >>> amount = Decimal('0.01')
    >>> gel_to_tetri(amount)
    1
    """
    return int(Decimal(amount).quantize(Decimal('1.00')) * 100)


def get_currency_code(code):
    """

    :param code: currency code or currency symbol
    :return: currency code
    """

    if code in CURRENCY_CODES:
        return code

    if code not in CURRENCY_SYMBOLS:
        raise ValueError('Invalid currency code, Allowed codes: GEL, USD, EUR')

    return ALLOW_CURRENCY_CODES[code]


def tbc_params(*arg_params, **kwarg_params):
    """
    Decorator that pops all accepted parameters from method's kwargs and puts
    them in the payload argument.
    """

    def wrapper(f):
        @wraps(f)
        def wrapped(*a, **kw):
            kw.update(kwarg_params)
            payload = dict()
            if 'payload' in kw:
                payload = kw.pop('payload')

            klass = a[0]
            if 'description' not in kw and 'description' in arg_params:
                payload['description'] = klass.description
            if 'client_ip_addr' in arg_params:
                payload['client_ip_addr'] = klass.client_ip

            for param in arg_params + tuple(kwarg_params.keys()):
                if param in payload:
                    continue
                if param not in kw:
                    raise ValueError(
                        f'Invalid params, {param} is a required parameter.'
                    )

                if param == 'currency':
                    payload[param] = get_currency_code(kw[param])
                elif param == 'amount':
                    payload[param] = gel_to_tetri(kw[param])
                else:
                    payload[param] = kw[param]
            return f(payload=payload, *a, **kw)

        return wrapped

    return wrapper


def _request(**kw):

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for k, v in kw.items():
                if k in kwargs:
                    continue
                kwargs[k] = v
            klass = args[0]
            try:
                resp = requests.post(
                    klass.merchant_url, data=kwargs['payload'],
                    verify=kwargs['verify'], timeout=kwargs['timeout'],
                    cert=klass.cert
                )
                if resp.status_code == 200:
                    result = parse_response(resp.text)
                else:
                    result = {
                        'RESULT': resp.text,
                        'STATUS_CODE': resp.status_code,
                    }
            except requests.exceptions.RequestException as e:
                result = {
                    'RESULT': str(e)
                }
            return f(result=result, *args, **kwargs)

        return wrapped

    return wrapper
