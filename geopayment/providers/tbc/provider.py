# _*_ coding: utf-8 _*_

"""
Created on Apr 14, 2020

@author: Lasha Gogua
"""

from typing import Dict, Any, Optional, Tuple

from geopayment.providers.utils import _request, tbc_params


__all__ = ['TBCProvider']


class BaseTBCProvider(object):
    trans_id: str = None
    refund_trans_id: str = None

    def __init__(self) -> None:
        assert callable(self.description) is False, \
            '`description` must be property, not callable'
        assert callable(self.client_ip) is False, \
            '`client_ip` must be property, not callable'
        assert callable(self.cert) is False, \
            '`cert` must be property, not callable'
        assert callable(self.service_url) is False, \
            '`service_url` must be property, not callable'

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
    def service_url(self) -> str:
        """

        :return: merchant service url
        """
        raise NotImplementedError(
            'Provider needs implement `service_url` function'
        )


class TBCProvider(BaseTBCProvider):

    @tbc_params('amount', 'currency', 'client_ip_addr',
                'description', command='v', language='ka', msg_type='SMS')
    @_request(verify=False, timeout=(3, 10), method='post')
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
    @_request(verify=False, timeout=(3, 10), method='post')
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
    @_request(verify=False, timeout=(3, 10), method='post')
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
    @_request(verify=False, timeout=(3, 10), method='post')
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
    @_request(verify=False, timeout=(3, 10), method='post')
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
    @_request(verify=False, timeout=(3, 10), method='post')
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

    @tbc_params('amount', 'currency', 'client_ip_addr', 'description',
                'biller_client_id', 'expiry', 'perspayee_expiry', 'perspayee_gen',
                command='z', language='ka', msg_type='SMS')
    @_request(verify=False, timeout=(3, 10), method='post')
    def card_register_with_deduction(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        language: The language of the transaction performed
        msg_type: Transaction authorization type

        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.card_register_with_deduction(amount=23.45, currency='GEL')
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        """
        return kwargs['result']

    @tbc_params('currency', 'client_ip_addr', 'description', 'biller_client_id',
                'expiry', 'perspayee_expiry', 'perspayee_gen',
                command='p', language='ka', msg_type='AUTH')
    @_request(verify=False, timeout=(3, 10), method='post')
    def card_register_with_zero_auth(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        language: The language of the transaction performed
        msg_type: Transaction authorization type

        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.card_register_with_auth(currency='GEL')
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        """
        return kwargs['result']

    @tbc_params('amount', 'currency', 'client_ip_addr', 'description',
                'biller_client_id', command='e', language='ka')
    @_request(verify=False, timeout=(3, 10), method='post')
    def recurring_payment(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type
        language: The language of the transaction performed

        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.recurring_payment(amount=23.6, currency='GEL')
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        RESULT         - operation result
        RESULT_CODE    - operation result code
        RRN            - rrn
        APPROVAL_CODE  - operation approval code
        error          - in case of an error

        """
        result = kwargs['result']
        if 'TRANSACTION_ID' in result:
            self.trans_id = result['TRANSACTION_ID']
        return result

    @tbc_params('amount', 'trans_id', command='g')
    @_request(verify=False, timeout=(3, 10), method='post')
    def refund_to_debit_card(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        command: Transaction type

        :param kwargs: Other operation parameters
        :return: Refund transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> trans_id = 'NMQfTRLUTne3eywr9YnAU78Qxxw='
        >>> provider.refund_to_debit_card(amount=23.6, trans_id=trans_id)
        {'REFUND_TRANS_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        REFUND_TRANS_ID - refund transaction identifier
        RESULT          - operation result
        RESULT_CODE     - operation result code
        error           - in case of an error

        """
        if 'trans_id' in kwargs:
            self.trans_id = kwargs['trans_id']
        result = kwargs['result']
        if 'REFUND_TRANS_ID' in result:
            self.refund_trans_id = result['REFUND_TRANS_ID']
        return result

    @tbc_params(command='b')
    @_request(verify=False, timeout=(3, 10), method='post')
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
