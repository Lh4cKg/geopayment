from __future__ import annotations

import typing as t
from decimal import Decimal

from geopayment.providers.request import Request
from geopayment.providers.tbc.base import BaseTBCPayProvider
from geopayment.providers.tbc.models.request import (
    Create,
    Status,
    Refund,
    Reversal,
    RefundToDebitCard,
    Recurring,
    CardRegister,
    CardRegisterConfirm,
    PreAuth,
    PreAuthConfirm,
    PreAuthRecurring,
    PreAuthCardRegisterConfirm,
    EndOfBusinessDay,
)
from geopayment.providers.tbc.models.response import (
    ErrorResponse,
    CreateResponse,
    StatusResponse,
    PreAuthResponse,
    PreAuthConfirmResponse,
    RefundResponse,
    ReversalResponse,
    EndBusinessDayResponse,
)
from geopayment.utils.currency import gel_to_tetri, get_currency_code
from geopayment.utils.serialize import to_dict


__all__ = ['TBCProvider']

from providers.tbc.models.response import SuccessResponse


class TBCProvider(BaseTBCPayProvider):

    def create(
            self,
            *,
            amount: Decimal,
            currency: str | int,
            client_ip_addr: str = None,
            description: str = None,
            language: t.Literal['ka', 'en'] = 'ka',
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> CreateResponse | ErrorResponse:
        """
        :param amount: The full amount is to be paid.
        :param currency: A payment currency
        :param language: The language of the transaction performed
        :param client_ip_addr:
        :param description: transaction description
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        >>> provider = MyTBCProvider()
        >>> provider.create_transaction(amount=23.45, currency='GEL')
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        :return: AuthResponse
        """

        if not client_ip_addr:
            client_ip_addr = self.config.client_ip

        if not description:
            description = self.config.description
        data = Create(
            command=self.command.create,
            amount=gel_to_tetri(amount),
            currency=get_currency_code(currency),
            client_ip_addr=client_ip_addr,
            description=description,
            language=language,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.create, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return CreateResponse(
            message=response.text, status_code=response.status_code
        )

    def status(
            self,
            *,
            transaction_id: str,
            client_ip_addr: str = None,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> StatusResponse | ErrorResponse:
        """
        :param transaction_id: created transaction identifier
        :param client_ip_addr:
        :param verify: in which case it controls whether we verify
        the server's TLS certificate
        :type verify: bool
        :param timeout: How many seconds to wait for the server to send data
        before giving up
        :type timeout: int or Tuple[int, int]

        >>> provider = MyTBCProvider()
        >>> trans = provider.create_transaction(amount=23.45, currency='GEL')
        >>> provider.transaction_status(trans_id=trans.trans_id)
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

        if not client_ip_addr:
            client_ip_addr = self.config.client_ip

        data = Status(
            command=self.command.status,
            trans_id=transaction_id,
            client_ip_addr=client_ip_addr,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.status, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return StatusResponse(
            message=response.text, status_code=response.status_code
        )

    def reversal(
            self,
            *,
            amount: Decimal,
            transaction_id: str,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> ReversalResponse | ErrorResponse:
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

        data = Reversal(
            command=self.command.reversal,
            trans_id=transaction_id,
            amount=gel_to_tetri(amount),
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.reversal, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return ReversalResponse(
            message=response.text, status_code=response.status_code
        )

    def refund(
            self,
            *,
            amount: Decimal,
            transaction_id: str,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> RefundResponse | ErrorResponse:
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

        data = Refund(
            command=self.command.refund,
            trans_id=transaction_id,
            amount=gel_to_tetri(amount),
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.refund, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return RefundResponse(
            message=response.text, status_code=response.status_code
        )

    def pre_auth(
            self,
            *,
            amount: Decimal,
            currency: str | int,
            description: str = None,
            client_ip_addr: str = None,
            language: t.Literal['ka', 'en'] = 'ka',
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> PreAuthResponse | ErrorResponse:
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

        if client_ip_addr is None:
            client_ip_addr = self.config.client_ip
        if description is None:
            description = self.config.description

        data = PreAuth(
            command=self.command.pre_auth,
            amount=gel_to_tetri(amount),
            currency=get_currency_code(currency),
            description=description,
            client_ip_addr=client_ip_addr,
            language=language,
            msg_type=self.message_type.dms,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.pre_auth, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return PreAuthResponse(
            message=response.text, status_code=response.status_code
        )

    def pre_auth_confirm(
            self,
            *,
            transaction_id: str,
            amount: Decimal,
            currency: str | int,
            description: str = None,
            client_ip_addr: str = None,
            language: t.Literal['ka', 'en'],
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> PreAuthConfirmResponse | ErrorResponse:
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
        if client_ip_addr is None:
            client_ip_addr = self.config.client_ip
        if description is None:
            description = self.config.description

        data = PreAuthConfirm(
            command=self.command.pre_auth_confirm,
            trans_id=transaction_id,
            amount=gel_to_tetri(amount),
            currency=get_currency_code(currency),
            description=description,
            client_ip_addr=client_ip_addr,
            language=language,
            msg_type=self.message_type.dms,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.pre_auth_confirm, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return PreAuthConfirmResponse(
            message=response.text, status_code=response.status_code
        )

    def card_register_confirm(
            self,
            *,
            amount: Decimal,
            currency: str | int,
            description: str,
            client_ip_addr: str,
            biller_client_id: str,
            expiry: str,
            perspayee_expiry: str,
            perspayee_gen: str,
            language: t.Literal['ka', 'en'] = 'ka',
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> SuccessResponse | ErrorResponse:
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
        data = CardRegisterConfirm(
            command=self.command.card_register_confirm,
            amount=gel_to_tetri(amount),
            currency=get_currency_code(currency),
            description=description,
            client_ip_addr=client_ip_addr,
            language=language,
            biller_client_id=biller_client_id,
            expiry=expiry,
            perspayee_expiry=perspayee_expiry,
            perspayee_gen=perspayee_gen,
            msg_type=self.message_type.sms,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.card_register_confirm, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return SuccessResponse(
            message=response.text, status_code=response.status_code
        )

    def pre_auth_card_register_confirm(
            self,
            *,
            amount: Decimal,
            currency: str | int,
            description: str,
            client_ip_addr: str,
            biller_client_id: str,
            expiry: str,
            perspayee_expiry: str,
            perspayee_gen: str,
            language: t.Literal['ka', 'en'] = 'ka',
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> SuccessResponse | ErrorResponse:
        """
        command: Transaction type
        language: The language of the transaction performed
        msg_type: Transaction authorization type

        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.pre_auth_card_register_with_deduction(amount=23.45, currency='GEL')
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        error          - in case of an error

        """
        data = PreAuthCardRegisterConfirm(
            command=self.command.pre_auth_card_register_confirm,
            amount=gel_to_tetri(amount),
            currency=get_currency_code(currency),
            description=description,
            client_ip_addr=client_ip_addr,
            language=language,
            biller_client_id=biller_client_id,
            expiry=expiry,
            perspayee_expiry=perspayee_expiry,
            perspayee_gen=perspayee_gen,
            msg_type=self.message_type.dms,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.pre_auth_card_register_confirm, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return SuccessResponse(
            message=response.text, status_code=response.status_code
        )

    def card_register(
            self,
            *,
            currency: str | int,
            description: str,
            client_ip_addr: str,
            biller_client_id: str,
            expiry: str,
            perspayee_expiry: str,
            perspayee_gen: str,
            language: t.Literal['ka', 'en'] = 'ka',
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> SuccessResponse | ErrorResponse:
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

        data = CardRegister(
            command=self.command.card_register,
            currency=get_currency_code(currency),
            description=description,
            client_ip_addr=client_ip_addr,
            language=language,
            biller_client_id=biller_client_id,
            expiry=expiry,
            perspayee_expiry=perspayee_expiry,
            perspayee_gen=perspayee_gen,
            msg_type=self.message_type.auth,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.card_register, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return SuccessResponse(
            message=response.text, status_code=response.status_code
        )

    def recurring(
            self,
            *,
            amount: Decimal,
            currency: str | int,
            description: str,
            client_ip_addr: str,
            biller_client_id: str,
            language: t.Literal['ka', 'en'] = 'ka',
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> SuccessResponse | ErrorResponse:
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
        data = Recurring(
            command=self.command.recurring,
            amount=gel_to_tetri(amount),
            currency=get_currency_code(currency),
            description=description,
            client_ip_addr=client_ip_addr,
            language=language,
            biller_client_id=biller_client_id,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.recurring, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return SuccessResponse(
            message=response.text, status_code=response.status_code
        )

    def pre_auth_recurring(
            self,
            *,
            amount: Decimal,
            currency: str | int,
            description: str,
            client_ip_addr: str,
            biller_client_id: str,
            language: t.Literal['ka', 'en'] = 'ka',
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> SuccessResponse | ErrorResponse:
        """
        command: Transaction type
        language: The language of the transaction performed

        :param kwargs: Other operation parameters
        :return: Transaction id from merchant response

        >>> provider = MyTBCProvider()
        >>> provider.pre_auth_recurring_payment(amount=23.6, currency='GEL')
        {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

        TRANSACTION_ID - transaction identifier
        RESULT         - operation result
        RESULT_CODE    - operation result code
        RRN            - rrn
        APPROVAL_CODE  - operation approval code
        error          - in case of an error

        """
        data = PreAuthRecurring(
            command=self.command.pre_auth_recurring,
            amount=gel_to_tetri(amount),
            currency=get_currency_code(currency),
            description=description,
            client_ip_addr=client_ip_addr,
            language=language,
            biller_client_id=biller_client_id,
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.pre_auth_recurring, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return SuccessResponse(
            message=response.text, status_code=response.status_code
        )

    def refund_to_debit_card(
            self,
            *,
            transaction_id: str,
            amount: Decimal,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> RefundResponse | ErrorResponse:
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
        data = RefundToDebitCard(
            command=self.command.refund_to_debit_card,
            trans_id=transaction_id,
            amount=gel_to_tetri(amount),
        )
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.refund_to_debit_card, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return RefundResponse(
            message=response.text, status_code=response.status_code
        )



    def end_of_business_day(
            self,
            *,
            verify: bool = True,
            timeout: t.Tuple[int, int] | int = (3, 10)
    ) -> EndBusinessDayResponse | ErrorResponse:
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
        data = EndOfBusinessDay(command=self.command.end_business_day)
        response = self.perform_request(data, verify, timeout)
        self._set_original_response(self.end_of_business_day, response)
        if response.status_code != 200:
            return ErrorResponse(
                message=response.text, status_code=response.status_code
            )
        return EndBusinessDayResponse(
            message=response.text, status_code=response.status_code
        )
