# _*_ coding: utf-8 _*_

"""
Created on Apr 14, 2020

@author: Lasha Gogua
"""

from typing import Dict, Any, Optional, Tuple

from payments.utils import tbc_params, _request


class BaseTBCMerchant(object):
    trans_id: str = None

    @property
    def description(self) -> str:
        raise NotImplementedError(
            'Merchant needs implement `description` function'
        )

    @property
    def client_ip(self) -> str:
        raise NotImplementedError(
            'Merchant needs implement `client_ip` function'
        )

    @property
    def cert(self) -> Tuple[str, str]:
        """
        certificate path
        :return: certificate as tuple (cert, key)
        """
        raise NotImplementedError(
            'Merchant needs implement `cert` function'
        )

    @property
    def merchant_url(self) -> str:
        """
        merchant
        :return:
        """
        raise NotImplementedError(
            'Merchant needs implement `merchant_url` function'
        )


class TBCMerchant(BaseTBCMerchant):

    @tbc_params('command', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    @_request(verify=False, timeout=(3, 10))
    def get_trans_id(self, command: str = 'v', language: str = 'ka',
                     msg_type: str = 'SMS',
                     **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        :param command: Transaction type
        :param language: The language of the transaction performed
        :param msg_type: Transaction authorization type
        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>>
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        """

        return kwargs['result']

    @tbc_params('command', 'trans_id', 'client_ip_addr')
    @_request(verify=False, timeout=(3, 10))
    def check_trans_status(self, command: str = 'c',
                           **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        :param command: Transaction type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>>
        {'RESULT': 'OK', 'RESULT_CODE': '000', '3DSECURE': 'ATTEMPTED',
        'CARD_NUMBER': '', 'RRN': '', 'APPROVAL_CODE': ''}

        RESULT             - transaction status
        RESULT_CODE        - transaction result code
        3DSECURE           - 3D Secure authorization
        RRN                - retrieval reference number
        APPROVAL_CODE      - approval code
        CARD_NUMBER        - masked card number
        error              - in case of an error
        warning            - in case of warning

        """

        return kwargs['result']

    @tbc_params('command', 'trans_id', 'amount')
    @_request(verify=False, timeout=(3, 10))
    def reversal_trans(self, command: str = 'r',
                       **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        :param command: Transaction type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>>
        {'RESULT': 'OK', 'RESULT_CODE': ''}

        RESULT         - reversal transaction status
        RESULT_CODE    - reversal result code
        error          - in case of an error
        warning        - in case of warning

        """

        return kwargs['result']

    @tbc_params('command', 'trans_id', 'amount')
    @_request(verify=False, timeout=(3, 10))
    def refund_trans(self, command: str = 'k',
                     **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        :param command: Transaction type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>>
        {'RESULT': '', 'RESULT_CODE': '', 'REFUND_TRANS_ID': ''}

        RESULT              - refund transaction status
        RESULT_CODE         - refund result code
        REFUND_TRANS_ID     - refund transaction identifier
        error               - in case of an error
        warning             - in case of warning

        """

        return kwargs['result']

    @tbc_params('command', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    @_request(verify=False, timeout=(3, 10))
    def dms_auth(self, command: str = 'a', language: str = 'ka',
                 msg_type: str = 'DMS',
                 **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        :param command: Transaction type
        :param language: The language of the transaction performed
        :param msg_type: Transaction authorization type
        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>>
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        """

        return kwargs['result']

    @tbc_params('command', 'trans_id', 'amount', 'currency', 'client_ip_addr',
                'language', 'description', 'msg_type')
    @_request(verify=False, timeout=(3, 10))
    def confirm_dms_trans(self, command: str = 't', language: str = 'ka',
                          msg_type: str = 'DMS',
                          **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        :param command: Transaction type
        :param language: The language of the transaction performed
        :param msg_type: Transaction authorization type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>>
        {'RESULT': 'OK', 'RESULT_CODE': '', 'BRN': '' 'APPROVAL_CODE': '',
         'CARD_NUMBER': ''}

        RESULT          - DMS transaction status
        RESULT_CODE     - DMS transaction result code
        BRN             - retrieval reference number
        APPROVAL_CODE   - approval code
        CARD_NUMBER     - masked card number
        error           - in case of an error

        """

        return kwargs['result']

    @tbc_params('command')
    @_request(verify=False, timeout=(3, 10))
    def end_of_business_day(self, command: str = 'b',
                            **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        :param command: Transaction type
        :param kwargs: Other operation parameters
        :return: End of business day status codes from merchant response

        >>>
        {'RESULT': 'OK', 'RESULT_CODE': '500', 'FLD_086': '0', 'FLD_089': '0',
        'FLD_076': '10', 'FLD_075': '5', 'FLD_088': '10', 'FLD_077': '0',
        'FLD_074': '0', 'FLD_087': '5'}

        RESULT          - end of business day status
        RESULT_CODE     - end of business day result code
        FLD_074         -
        FLD_075         - the number of credit reversals
        FLD_076         - the number of debit transactions
        FLD_077         -
        FLD_086         -
        FLD_087         - total amount of credit reversals
        FLD_088         - total amount of debit transactions
        FLD_089         -

        """

        return kwargs['result']

    @classmethod
    def quick_end_of_business_day(cls):
        """
        This function is same as `end_of_business_day` for quick call end of
        business day command.

        :return: End of business day status codes from merchant response
        """
        return cls().end_of_business_day()
