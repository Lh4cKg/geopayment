# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

import json
from decimal import Decimal, ROUND_UP
from functools import wraps
from typing import Dict, Any, Union

import requests


from geopayment.constants import (
    CURRENCY_CODES,
    CURRENCY_SYMBOLS,
    ALLOW_CURRENCY_CODES,
    DEFAULT_PAYLOAD_ARGS,
    BOG_ITEM_KEYS,
    BOG_INSTALLMENT_ITEM_KEYS
)


def get_client_ip(request) -> str:
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


def parse_response(content: str) -> Dict:
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


def gel_to_tetri(
        amount: Union[int, float, Decimal],
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


def _request(**kw):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            request_params: Dict[str, Any] = dict()
            for k, v in kw.items():
                if k in kwargs:
                    continue
                kwargs[k] = v

            klass = args[0]
            method = kwargs['method']
            request_params['url'] = kwargs.get('url', klass.service_url)
            request_params['method'] = method
            request_params.update(kwargs['payload'])
            request_params['headers'] = kwargs.get('headers')
            request_params['verify'] = kwargs['verify']
            request_params['timeout'] = kwargs['timeout']
            request_params['cert'] = getattr(klass, 'cert', None)
            if method == 'get':
                request_params['allow_redirects'] = True

            try:
                resp = requests.request(**request_params)
                if resp.status_code == 200:
                    try:
                        result = resp.json()
                    except (ValueError, json.decoder.JSONDecodeError):
                        result = parse_response(resp.text)
                    except Exception:
                        result = resp.text
                else:
                    try:
                        result = resp.json()
                    except (ValueError, json.decoder.JSONDecodeError):
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
                payload = kw.pop('payload', dict())
            payload.update(kwarg_params)

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
            return f(payload={'data': payload}, *a, **kw)

        return wrapped

    return wrapper


def bog_params(**kw):
    """
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
            data, headers, payload = dict(), dict(), dict()
            endpoint = kw['endpoint']
            api = kw['api']
            if api == 'auth':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                credentials = klass.get_credentials().decode('utf-8')
                headers['Authorization'] = f'Basic {credentials}'
                if 'grant_type' in kwargs:
                    data['grant_type'] = kwargs['grant_type']
                else:
                    data['grant_type'] = 'client_credentials'
                payload.update({'data': data})
            elif api == 'checkout':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'
                if 'intent' in kwargs:
                    data['intent'] = kwargs['intent']
                else:
                    data['intent'] = 'AUTHORIZE'  # 'CAPTURE'

                if 'redirect_url' in kwargs:
                    data['redirect_url'] = kwargs['redirect_url']
                else:
                    data['redirect_url'] = klass.redirect_url

                if 'shop_order_id' in kwargs:
                    data['shop_order_id'] = kwargs['shop_order_id']
                if 'card_transaction_id' in kwargs:
                    data['card_transaction_id'] = kwargs['card_transaction_id']
                if 'locale' in kwargs:
                    data['locale'] = kwargs['locale']

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
                data['items'] = kwargs['items']
                data['purchase_units'] = [
                    {
                        'amount': {
                            'currency_code': kwargs['currency_code'],
                            'value': str(amount.quantize(
                                Decimal('.00'), rounding=ROUND_UP
                            ))
                        },
                        'industry_type': 'ECOMMERCE'
                    }
                ]
                payload.update({'json': data})
            elif api == 'installment-checkout':
                """
                {
                  "intent": "LOAN",
                  "installment_month": 6,
                  "installment_type": "STANDARD",
                  "shop_order_id": "123456",
                  "success_redirect_url": "https://demo.ipay.ge/success",
                  "fail_redirect_url": "https://demo.ipay.ge/fail",
                  "reject_redirect_url": "https://demo.ipay.ge/reject",
                  "validate_items": true,
                  "locale": "ka",
                  "purchase_units": [
                    {
                      "amount": {
                        "currency_code": "GEL",
                        "value": "500.00"
                      }
                    }
                  ],
                  "cart_items": [
                    {
                      "total_item_amount": "10.50",
                      "item_description": "test_product",
                      "total_item_qty": "1",
                      "item_vendor_code": "123456",
                      "product_image_url": "https://example.com/product.jpg",
                      "item_site_detail_url": "https://example.com/product"
                    }
                  ]
                }
                """
                error_message = (
                    'Invalid params, `{0}` is a required parameter. '
                    'Read api docs <https://api.bog.ge/docs/installment/create-order>.'
                )
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'

                data['intent'] = kwargs.get('intent', 'LOAN')
                if 'installment_month' in kwargs:
                    data['installment_month'] = kwargs['installment_month']
                else:
                    raise ValueError(error_message.format('installment_month'))

                if 'installment_type' in kwargs:
                    data['installment_type'] = kwargs['installment_type']
                else:
                    raise ValueError(error_message.format('installment_type'))

                if 'shop_order_id' in kwargs:
                    data['shop_order_id'] = kwargs['shop_order_id']
                else:
                    raise ValueError(error_message.format('shop_order_id'))

                data['success_redirect_url'] = kwargs.get('success_redirect_url', klass.redirect_url)
                data['fail_redirect_url'] = kwargs.get('fail_redirect_url', klass.redirect_url)
                data['reject_redirect_url'] = kwargs.get('reject_redirect_url', klass.redirect_url)
                data['validate_items'] = kwargs.get('validate_items', True)
                data['locale'] = kwargs.get('locale', klass.default_locale)

                if 'cart_items' not in kwargs:
                    raise ValueError(error_message.format('cart_items'))

                data['cart_items'] = kwargs['cart_items']
                amount = Decimal(0)
                for item in kwargs['cart_items']:
                    for key in BOG_INSTALLMENT_ITEM_KEYS:
                        if key not in item:
                            raise ValueError(error_message.format(key))
                    amount += Decimal(item['total_item_amount'])
                    item['total_item_amount'] = str(item['total_item_amount'])

                if 'currency_code' not in kwargs:
                    raise ValueError(error_message.format('currency_code'))
                if 'purchase_units' not in kwargs:
                    data['purchase_units'] = [{
                        'amount': {
                            'currency_code': kwargs['currency_code'],
                            'value': str(amount.quantize(Decimal('.00'), rounding=ROUND_UP))
                        },
                    }]

                payload.update({'json': data})
            elif api == 'installment-calculate':
                if 'amount' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `amount` is a required parameter.'
                    )
                data['amount'] = str(kwargs['amount'])

                if 'client_id' not in kwargs:
                    data['client_id'] = klass.client_id
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'
                payload.update({'json': data})
            elif api == 'refund':
                if 'order_id' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `order_id` is a required parameter.'
                    )
                if 'amount' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `amount` is a required parameter.'
                    )
                data = {
                    'order_id': kwargs['order_id'],
                    'amount': kwargs['amount'],
                }
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                payload.update({'data': data})
            elif api in ('status', 'details', 'payment'):
                if 'order_id' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `order_id` is a required parameter.'
                    )
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'
                endpoint = endpoint.format(order_id=kwargs['order_id'])
            else:
                raise ValueError(
                    'Unsupported `api` type.'
                )

            if api != 'auth':
                try:
                    if 'access_token' not in kwargs:
                        access_token = klass.access['access_token']
                    else:
                        access_token = kwargs['access_token']
                except TypeError:
                    raise ValueError(
                        'Invalid params, `access_token` is a required parameter. '
                        'Use authorization method `get_auth` or set `access_token` value.'
                    )
                headers['Authorization'] = f'Bearer {access_token}'

            kwargs = {
                'url': f'{klass.service_url}{endpoint}',
                'headers': headers
            }

            return f(payload=payload, *args, **kwargs)

        return wrapped

    return wrapper
