# _*_ coding: utf-8 _*_

"""
Created on Apr 14, 2020

@author: Lasha Gogua
"""

from typing import Dict, Any, Optional, Tuple

from payments.utils import tbc_params, _request


class BaseTBCMerchant(object):
    results: Dict[str, Any] = None
    trans_id: str = None

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
                     msg_type: str = 'SMS',
                     **kwargs: Optional[Any]) -> Dict[str, str]:
        pass

    @tbc_params('command', 'trans_id', 'client_ip_addr')
    @_request(verify=False, timeout=(3, 10))
    def check_trans_status(self, command: str = 'c',
                           **kwargs: Optional[Any]) -> Dict[str, str]:
        pass

    @tbc_params('command', 'trans_id', 'amount')
    @_request(verify=False, timeout=(3, 10))
    def reversal_trans(self, command: str = 'r', **kwargs) -> Dict[str, str]:
        pass

    @tbc_params('command', 'trans_id', 'amount')
    @_request(verify=False, timeout=(3, 10))
    def refund_trans(self, command: str = 'k', **kwargs) -> Dict[str, str]:
        pass

    @tbc_params('command', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    @_request(verify=False, timeout=(3, 10))
    def dms_auth(self, command: str = 'a', language: str = 'ka',
                 msg_type: str = 'DMS',
                 **kwargs: Optional[Any]) -> Dict[str, str]:
        pass

    @tbc_params('command', 'trans_id', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    @_request(verify=False, timeout=(3, 10))
    def confirm_dms_trans(self, command: str = 't', language: str = 'ka',
                          msg_type: str = 'DMS',
                          **kwargs: Optional[Any]) -> Dict[str, str]:
        pass

    @classmethod
    @tbc_params('command')
    @_request(verify=False, timeout=(3, 10))
    def end_of_business_day(cls, command: str = 'b',
                            **kwargs: Optional[Any]) -> Dict[str, str]:
        pass

