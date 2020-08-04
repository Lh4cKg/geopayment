# _*_ coding: utf-8 _*_

"""
Created on Apr 14, 2020

@author: Lasha Gogua
"""

from typing import Dict, Any, Optional, Tuple

from geopayment.providers.utils import tbc_params, tbc_request


class BaseTBCProvider(object):
    trans_id: str = None

    def __init__(self) -> None:
        assert callable(self.description) is False, \
            '`description` must be property, not callable'
        assert callable(self.client_ip) is False, \
            '`client_ip` must be property, not callable'
        assert callable(self.cert) is False, \
            '`cert` must be property, not callable'
        assert callable(self.merchant_url) is False, \
            '`merchant_url` must be property, not callable'

    @property
    def description(self) -> str:
        """

        :return: merchant description
        """
        raise NotImplementedError(
            'Provider needs implement `description` function'
        )

    @property
    def client_ip(self) -> str:
        """
        client accepted ip address
        :return:
        """
        raise NotImplementedError(
            'Provider needs implement `client_ip` function'
        )

    @property
    def cert(self) -> Tuple[str, str]:
        """
        Certificate path
        :return: certificate as tuple (cert, key)
        """
        raise NotImplementedError(
            'Provider needs implement `cert` function'
        )

    @property
    def merchant_url(self) -> str:
        """

        :return: merchant service url
        """
        raise NotImplementedError(
            'Provider needs implement `merchant_url` function'
        )


class TBCProvider(BaseTBCProvider):

    @tbc_params('amount', 'currency', 'client_ip_addr',
                'description', command='v', language='ka', msg_type='SMS')
    @tbc_request(verify=False, timeout=(3, 10))
    def get_trans_id(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        language: The language of the transaction performed
        msg_type: Transaction authorization type

        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.get_trans_id(amount=23.45, currency='GEL')
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        """

        result = kwargs['result']
        if 'TRANSACTION_ID' in result:
            self.trans_id = result['TRANSACTION_ID']
        return result

    @tbc_params('trans_id', 'client_ip_addr', command='c')
    @tbc_request(verify=False, timeout=(3, 10))
    def check_trans_status(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.get_trans_id(amount=23.45, currency='GEL')
        >>> provider.check_trans_status(trans_id=provider.trans_id)
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

    @tbc_params('trans_id', 'amount', command='r')
    @tbc_request(verify=False, timeout=(3, 10))
    def reversal_trans(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.get_trans_id(amount=23.45, currency='GEL')
        >>> provider.reversal_trans(trans_id=provider.trans_id, amount=12.20)
        {'RESULT': 'OK', 'RESULT_CODE': ''}

        RESULT         - reversal transaction status
        RESULT_CODE    - reversal result code
        error          - in case of an error
        warning        - in case of warning

        """

        return kwargs['result']

    @tbc_params('trans_id', 'amount', command='k')
    @tbc_request(verify=False, timeout=(3, 10))
    def refund_trans(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.get_trans_id(amount=23.45, currency='GEL')
        >>> provider.refund_trans(trans_id=provider.trans_id, amount=23.45)
        {'RESULT': '', 'RESULT_CODE': '', 'REFUND_TRANS_ID': ''}

        RESULT              - refund transaction status
        RESULT_CODE         - refund result code
        REFUND_TRANS_ID     - refund transaction identifier
        error               - in case of an error
        warning             - in case of warning

        """

        return kwargs['result']

    @tbc_params('amount', 'currency', 'client_ip_addr', 'description',
                command='a', language='ka', msg_type='DMS')
    @tbc_request(verify=False, timeout=(3, 10))
    def pre_auth_trans(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        language: The language of the transaction performed
        msg_type: Transaction authorization type
        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.pre_auth_trans(amount=23.45, currency=981)
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        """

        result = kwargs['result']
        if 'TRANSACTION_ID' in result:
            self.trans_id = result['TRANSACTION_ID']
        return result

    @tbc_params('trans_id', 'amount', 'currency', 'client_ip_addr',
                'description', command='t', language='ka', msg_type='DMS')
    @tbc_request(verify=False, timeout=(3, 10))
    def confirm_pre_auth_trans(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        language: The language of the transaction performed
        msg_type: Transaction authorization type
        :param kwargs: Other operation parameters
        :return: Transaction status codes from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.pre_auth_trans(amount=23.45, currency=981)
        >>> provider.confirm_pre_auth_trans(trans_id=provider.trans_id, amount=23.45, currency=981)
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

    @tbc_params(command='b')
    @tbc_request(verify=False, timeout=(3, 10))
    def end_of_business_day(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        :param kwargs: Other operation parameters
        :return: End of business day status codes from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.end_of_business_day()
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
    def quick_end_of_business_day(cls) -> Dict[str, str]:
        """
        This function is same as `end_of_business_day` for quick call end of
        business day command.

        :return: End of business day status codes from merchant response
        """
        return cls().end_of_business_day()
