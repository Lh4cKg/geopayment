# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

from decimal import Decimal
from functools import wraps
import requests

from payments.constants import CURRENCY_CODES, ALLOW_CURRENCY_CODES


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

    return ALLOW_CURRENCY_CODES.get(code)


def tbc_params(*params):
    """
    Decorator that pops all accepted parameters from method's kwargs and puts
    them in the payload argument.
    """

    def wrapper(f):
        @wraps(f)
        def wrapped(*a, **kw):
            payload = dict()
            if 'payload' in kw:
                payload = kw.pop('payload')

            klass = a[0]
            if 'description' not in kw:
                kw['description'] = klass.description

            for param in params:
                if param not in kw:
                    if param == 'client_ip_addr':
                        kw['client_ip_addr'] = klass.client_ip
                    else:
                        raise ValueError(
                            f'Invalid params, {param} is a required parameter.'
                        )
                if param in payload:
                    continue

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
            klass = args[0]
            try:
                resp = requests.post(
                    klass.merchant_url, data=kw['payload'],
                    verify=kw['verify'], timeout=kw['timeout'],
                    cert=klass.cert
                )
                if resp.status_code == 200:
                    result = parse_response(resp.text)
                else:
                    result = {
                        'result': resp.text,
                        'status_code': resp.status_code,
                    }
            except requests.exceptions.RequestException:
                result = {
                    'result': 'error',
                    'error_type': 'timeout',
                    'status_code': 408,
                }
            return f(result=result, *args, **kwargs)

        return wrapped

    return wrapper
