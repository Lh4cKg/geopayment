# _*_ coding: utf-8 _*_

"""
Created on Apr 14, 2020

@author: Lasha Gogua
"""

from base64 import b64encode
from typing import Optional, Any, Dict

from geopayment.providers.utils import _request, bog_params


__all__ = ['IPayProvider']


class BaseIPayProvider(object):
    access: Dict = None
    rel_approve: str = None
    order_status: str = None

    def __init__(self) -> None:
        assert callable(self.client_id) is False, \
            '`client_id` must be property, not callable'
        assert callable(self.secret_key) is False, \
            '`secret_key` must be property, not callable'
        assert callable(self.service_url) is False, \
            '`service_url` must be property, not callable'
        assert callable(self.redirect_url) is False, \
            '`redirect_url` must be property, not callable'

    @property
    def client_id(self) -> str:
        """

        :return: client id
        """
        raise NotImplementedError(
            'Provider needs implement `client_id` function'
        )

    @property
    def secret_key(self) -> str:
        """

        :return: client secret key
        """
        raise NotImplementedError(
            'Provider needs implement `secret_key` function'
        )

    @property
    def service_url(self) -> str:
        """

        :return: provider service url
        """
        raise NotImplementedError(
            'Provider needs implement `service_url` function'
        )

    @property
    def redirect_url(self) -> str:
        """

        :return: redirect success or fail url
        """
        raise NotImplementedError(
            'Provider needs implement `redirect_url` function'
        )

    def get_credentials(self) -> bytes:
        return b64encode(f'{self.client_id}:{self.secret_key}'.encode())


class IPayProvider(BaseIPayProvider):

    @bog_params(endpoint='oauth2/token', api='auth')
    @_request(verify=True, timeout=(3, 10), method='post')
    def get_auth(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        checkout api docs: https://developer.ipay.ge/checkout

        :param kwargs:
        :return: result
        """

        self.access = kwargs['result']
        return self.access

    @bog_params(currency_code='GEL', endpoint='checkout/orders', api='checkout')
    @_request(verify=True, timeout=(3, 10), method='post')
    def checkout(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        checkout api docs: https://developer.ipay.ge/checkout
        :param kwargs:
        :return:
        """

        result = kwargs['result']
        if 'status' in result:
            self.order_status = result['status']
        if 'links' in result and self.order_status:
            link = list(
                filter(lambda x: x['rel'] == 'approve', result['links'])
            )
            if link:
                self.rel_approve = link[0]['href']
        return result

    @bog_params(endpoint='checkout/refund', api='refund')
    @_request(verify=True, timeout=(3, 10), method='post')
    def refund(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """

        :param kwargs:
        :return:
        """

        return kwargs['result']

    @bog_params(endpoint='checkout/orders/status/{order_id}', api='status')
    @_request(verify=True, timeout=(3, 10), method='get')
    def checkout_status(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """

        :param kwargs:
        :return:
        """

        return kwargs['result']

    @bog_params(endpoint='checkout/orders/{order_id}', api='details')
    @_request(verify=True, timeout=(3, 10), method='get')
    def checkout_details(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """

        :param kwargs:
        :return:
        """

        return kwargs['result']

    @bog_params(endpoint='checkout/payment/{order_id}', api='payment')
    @_request(verify=True, timeout=(3, 10), method='get')
    def payment_details(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """

        :param kwargs:
        :return:
        """

        return kwargs['result']
