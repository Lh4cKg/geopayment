# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""
import datetime
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
    BOG_INSTALLMENT_ITEM_KEYS,
    TBC_INSTALLMENT_ITEM_KEYS
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


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, Decimal):
            return str(o)

        return super().default(o)


def perform_http_response(response: requests.Response):
    """
    :param response: Response object from HTTP Request
    :return: result from merchant handler
    """
    try:
        result = response.json()
        result.update({'HTTP_STATUS_CODE': response.status_code})
    except (ValueError, json.decoder.JSONDecodeError):
        result = parse_response(response.text)
        result.update({'HTTP_STATUS_CODE': response.status_code})
    except Exception as e:
        result = {
            'RESULT': response.text,
            'ERROR': str(e),
            'HTTP_STATUS_CODE': response.status_code
        }
    return result


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
            payload = kwargs['payload']
            if 'json' in payload:
                payload['json'] = json.loads(
                    json.dumps(payload.pop('json'), cls=JsonEncoder)
                )
            request_params.update(payload)
            request_params['headers'] = kwargs.get('headers')
            request_params['verify'] = kwargs.get('verify', True)
            request_params['timeout'] = kwargs.get('timeout', 4)
            request_params['cert'] = getattr(klass, 'cert', None)
            if method == 'get':
                request_params['allow_redirects'] = True

            try:
                resp = requests.request(**request_params)
                kwargs['HTTP_STATUS_CODE'] = resp.status_code
                result = perform_http_response(resp)
                kwargs['headers'] = resp.headers
            except requests.exceptions.RequestException as e:
                result = {'ERROR': str(e)}
                kwargs['headers'] = dict()
                if 'HTTP_STATUS_CODE' not in kwargs:
                    kwargs['HTTP_STATUS_CODE'] = 'N/A'

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


def tbc_installment_params(**kw):
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
            if endpoint.startswith('/'):
                raise ValueError(
                    '`endpoint` beginning with a "/". '
                    'Remove this slash it is unnecessary.'
                )
            api = kw['api']
            if api == 'auth':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                credentials = klass.get_basic_auth().decode('utf-8')
                headers['Authorization'] = f'Basic {credentials}'
                if 'grant_type' in kwargs:
                    data['grant_type'] = kwargs['grant_type']
                if 'scope' in kwargs:
                    data['scope'] = kwargs['scope']
                payload.update({'data': data})
            elif api == 'create':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'
                if 'merchant_key' in kwargs:
                    data['merchantKey'] = kwargs['merchant_key']
                else:
                    data['merchantKey'] = klass.merchant_key
                if 'campaign_id' in kwargs:
                    data['campaignId'] = kwargs['campaign_id']
                else:
                    data['campaignId'] = klass.campaign_id

                if 'products' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `products` is a required parameter.'
                    )
                if 'invoice_id' not in kwargs:
                    raise ValueError(
                        f'Invalid params, `invoice_id` is a required parameter.'
                    )
                else:
                    data['invoiceId'] = kwargs['invoice_id']
                amount = Decimal(0)
                for item in kwargs['products']:
                    for key in TBC_INSTALLMENT_ITEM_KEYS:
                        if key not in item:
                            raise ValueError(
                                f'Invalid params, products item `{key}` is a '
                                f'required parameter.'
                            )
                    amount += Decimal(item['price'])
                data['products'] = kwargs['products']
                data['priceTotal'] = str(amount.quantize(Decimal('.00')))

                payload.update({'json': data})
            elif api == 'confirm' or api == 'cancel' or api == 'status':
                endpoint = endpoint.format(session_id=klass.session_id)

                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'

                if 'merchant_key' in kwargs:
                    data['merchantKey'] = kwargs['merchant_key']
                else:
                    data['merchantKey'] = klass.merchant_key

                payload.update({'json': data})
            elif api == 'statuses':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'

                if 'merchant_key' in kwargs:
                    data['merchantKey'] = kwargs['merchant_key']
                else:
                    data['merchantKey'] = klass.merchant_key

                try:
                    data['take'] = kwargs.get('take', 15)
                except ValueError:
                    raise ValueError(
                        f'Invalid params, `take` must be integer.'
                    )

                payload.update({'json': data})
            elif api == 'status-sync':
                headers['accept'] = 'application/json'
                headers['Content-Type'] = 'application/json'

                if 'merchant_key' in kwargs:
                    data['merchantKey'] = kwargs['merchant_key']
                else:
                    data['merchantKey'] = klass.merchant_key

                if 'sync_request_id' in kwargs:
                    data['synchronizationRequestId'] = kwargs['sync_request_id']

                payload.update({'json': data})
            else:
                raise ValueError('Unsupported `api` type.')

            if api != 'auth':
                try:
                    if 'access_token' not in kwargs:
                        access_token = klass.auth.access_token
                    else:
                        access_token = kwargs['access_token']
                except TypeError:
                    raise ValueError(
                        'Invalid params, `access_token` is a required parameter. '
                        'Use authorization method `get_auth` or set `access_token` value.'
                    )
                headers['Authorization'] = f'Bearer {access_token}'

            kwargs = {
                'url': f'{klass.url}{endpoint}',
                'headers': headers
            }

            return f(payload=payload, *args, **kwargs)

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
                raise ValueError('Unsupported `api` type.')

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
