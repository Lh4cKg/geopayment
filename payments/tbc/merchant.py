# _*_ coding: utf-8 _*_

"""
Created on Apr 14, 2020

@author: Lasha Gogua
"""

from typing import Dict, Any, Optional, Tuple

from payments.utils import tbc_params, _request


class BaseTBCMerchant(object):
    trans_id = None

    @property
    def description(self) -> str:
        raise NotImplementedError

    @property
    def client_ip(self) -> str:
        raise NotImplementedError

    @property
    def cert(self) -> Tuple[str, str]:
        """
        certificate path
        :return: certificate as tuple (cert, key)
        """
        raise NotImplementedError

    @property
    def merchant_url(self) -> str:
        """
        merchant
        :return:
        """
        raise NotImplementedError


class TBCMerchant(BaseTBCMerchant):

    def __init__(self):
        pass

    @tbc_params('command', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    @_request(verify=False, timeout=(3, 10))
    def get_trans_id(self, command: str = 'v', language: str = 'ka',
                     msg_type: str = 'SMS', payload: Dict[str, Any] = None,
                     **kwargs: Optional[Any]) -> Dict[str, str]:
        pass

    @tbc_params('command', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    def check_trans_status(self, payload, **kwargs) -> Dict[str, str]:
        pass

    @tbc_params('command', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    def reversal_trans(self, payload, **kwargs) -> Dict[str, str]:
        pass

    @tbc_params('command', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    def refund_trans(self, payload, **kwargs) -> Dict[str, str]:
        pass

    @BaseTBCMerchant._request
    def dms_auth(self, payload, **kwargs) -> Dict[str, str]:
        pass

    def confirm_dms_trans(self, payload, **kwargs) -> Dict[str, str]:
        pass

    @classmethod
    def end_of_business_day(cls, **kwargs):
        pass

