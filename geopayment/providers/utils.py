# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

from decimal import Decimal
from functools import wraps
import requests

from geopayment.constants import (
    CURRENCY_CODES,
    CURRENCY_SYMBOLS,
    ALLOW_CURRENCY_CODES,
    DEFAULT_PAYLOAD_ARGS,
    BOG_ITEM_KEYS
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
                if param in payload or param in DEFAULT_PAYLOAD_ARGS:
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


def tbc_request(**kw):

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


def bog_request(**kw):
    """

        "https://dev.ipay.ge/opay/api/v1/oauth2/token"
        -H "accept: application/json"
        -H "Authorization: Basic your_secret_key_client_id_base64"
        -H "Content-Type: application/x-www-form-urlencoded"
        -d "grant_type=client_credentials"

    :param kw:
    :return:
    """

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for k, v in kw.items():
                if k in kwargs:
                    continue
                kwargs[k] = v

            klass = args[0]
            data, headers = dict(), dict()

            if 'token_type' in kwargs and kwargs['token_type'] == 'Basic':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                credentials = klass.get_credentials().decode('utf-8')
                headers['Authorization'] = f'Basic {credentials}'
                if 'grant_type' in kwargs:
                    data['grant_type'] = kwargs['grant_type']
                else:
                    data['grant_type'] = 'client_credentials'
            elif 'token_type' in kwargs and kwargs['token_type'] == 'Bearer':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'
                access_token = klass.access['access_token']
                headers['Authorization'] = f'Bearer {access_token}'
                if 'intent' in kwargs:
                    data['intent'] = kwargs['intent']
                else:
                    data['intent'] = 'CAPTURE'

                if 'redirect_url' in kwargs:
                    data['redirect_url'] = kwargs['redirect_url']
                else:
                    data['redirect_url'] = klass.redirect_url

                if 'shop_order_id' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `shop_order_id` is a '
                        f'required parameter.'
                    )
                data['shop_order_id'] = kwargs['shop_order_id']
                if 'items' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `items` is a required parameter.'
                    )
                amount = Decimal(0)
                for item in kwargs['items']:
                    for key in BOG_ITEM_KEYS:
                        if key not in item:
                            raise ValueError(
                                f'Invalid params, item `{key}` is a '
                                f'required parameter.'
                            )
                    amount += Decimal(item['amount'])

                data['purchase_units'] = [
                    {
                        'amount': {
                            'currency_code': kwargs['currency_code'],
                            'value': amount.quantize(Decimal('.00'))
                        },
                        'industry_type': 'ECOMMERCE'
                    }
                ]

            try:
                resp = requests.post(
                    f'{klass.merchant_url}{kwargs["endpoint"]}', data=data,
                    verify=kwargs['verify'], timeout=kwargs['timeout']
                )
                if resp.status_code == 200:
                    result = resp.json()
                elif resp.status_code == 400:
                    result = {
                        'RESULT': 'Bad request, missing parameters',
                        'STATUS_CODE': 400,
                    }
                elif resp.status_code == 401:
                    result = {
                        'RESULT': 'Unauthorized, missing basic '
                                  'authorization credentials',
                        'STATUS_CODE': 401,
                    }
                elif resp.status_code == 403:
                    result = {
                        'RESULT': 'Forbidden',
                        'STATUS_CODE': 403,
                    }
                elif resp.status_code == 405:
                    result = {
                        'RESULT': 'Method Not Allowed',
                        'STATUS_CODE': 405,
                    }
                elif resp.status_code == 406:
                    result = {
                        'RESULT': 'Method Not Acceptable',
                        'STATUS_CODE': 406,
                    }
                elif resp.status_code == 415:
                    result = {
                        'RESULT': 'Unsupported Media Type',
                        'STATUS_CODE': 415,
                    }
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
