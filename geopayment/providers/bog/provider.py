# _*_ coding: utf-8 _*_

"""
Created on Apr 14, 2020

@author: Lasha Gogua
"""

from base64 import b64encode
from typing import Optional, Any, Dict

from geopayment.providers.utils import bog_request


class BaseIPayProvider(object):
    access: Dict = None
    rel_approve: str = None
    order_status: str = None

    def __init__(self) -> None:
        assert callable(self.client_id) is False, \
            '`client_id` must be property, not callable'
        assert callable(self.secret_key) is False, \
            '`secret_key` must be property, not callable'
        assert callable(self.merchant_url) is False, \
            '`merchant_url` must be property, not callable'
        assert callable(self.redirect_url) is False, \
            '`redirect_url` must be property, not callable'

    @property
    def client_id(self) -> str:
        """
        client id
        :return:
        """
        raise NotImplementedError(
            'Provider needs implement `client_id` function'
        )

    @property
    def secret_key(self) -> str:
        """
        client secret key
        :return:
        """
        raise NotImplementedError(
            'Provider needs implement `secret_key` function'
        )

    @property
    def merchant_url(self) -> str:
        """

        :return: merchant service url
        """
        raise NotImplementedError(
            'Provider needs implement `merchant_url` function'
        )

    @property
    def redirect_url(self) -> str:
        """

        :return: redirect url of product
        """
        raise NotImplementedError(
            'Provider needs implement `redirect_url` function'
        )

    def get_credentials(self) -> bytes:
        return b64encode(f'{self.client_id}:{self.secret_key}'.encode())


class IPayProvider(BaseIPayProvider):

    @bog_request(verify=True, timeout=(3, 10), token_type='Basic',
                 endpoint='oauth2/token')
    def get_auth(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        checkout api docs: https://developer.ipay.ge/checkout

        :param kwargs:
        :return: result
        """

        self.access = kwargs['result']
        return self.access

    @bog_request(verify=True, timeout=(3, 10), token_type='Bearer',
                 currency_code='GEL', endpoint='checkout/orders')
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
