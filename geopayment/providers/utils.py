from decimal import Decimal
from functools import wraps

from geopayment.constants import (
    DEFAULT_PAYLOAD_ARGS,
    TBC_INSTALLMENT_ITEM_KEYS
)

# TODO !!! must be deleted !!!

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
