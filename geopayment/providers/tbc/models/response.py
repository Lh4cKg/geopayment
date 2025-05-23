import typing as t
from pydantic.dataclasses import dataclass

from geopayment.utils.common import parse_response


@dataclass
class AuthResponse:
    access_token: str
    token_type: str
    expires_in: int
    app_id: str | None = None
    status_code: int | None = None


@dataclass
class SuccessResponse:
    message: str
    status_code: int


@dataclass
class CreateResponse(SuccessResponse):
    transaction_id: str | None = None

    def __post_init__(self):
        data = parse_response(self.message.lower())
        self.transaction_id = data.get('transaction_id')

@dataclass
class StatusResponse(SuccessResponse):
    result: str | None = None
    result_code: str | None = None
    secure3d: str | None = None
    rrn: str | None = None
    approval_code: str | None = None
    card_number: str | None = None
    recc_pmnt_id: str | None = None
    recc_pmnt_expiry: str | None = None
    mrch_transaction_id: str | None = None

    def __post_init__(self):
        data = parse_response(self.message.lower())
        self.result = data.get('result')
        self.result_code = data.get('result_code')
        self.secure3d = data.get('3dsecure')
        self.rnn = data.get('rnn')
        self.approval_code = data.get('approval_code')
        self.card_number = data.get('card_number')
        self.recc_pmnt_id = data.get('recc_pmnt_id')
        self.recc_pmnt_expiry = data.get('recc_pmnt_expiry')
        self.mrch_transaction_id = data.get('mrch_transaction_id')


@dataclass
class ReversalResponse(CreateResponse):
    result: str | None = None
    result_code: str | None = None

    def __post_init__(self):
        data = parse_response(self.message.lower())
        self.result = data.get('result')
        self.result_code = data.get('result_code')


@dataclass
class RefundResponse(CreateResponse):
    result: str | None = None
    result_code: str | None = None
    transaction_id: str | None = None

    def __post_init__(self):
        data = parse_response(self.message.lower())
        self.result = data.get('result')
        self.result_code = data.get('result_code')
        self.transaction_id = data.get('refund_trans_id')


@dataclass
class PreAuthResponse(CreateResponse):
    pass


@dataclass
class PreAuthConfirmResponse(SuccessResponse):
    result: t.Literal['ok', 'failed'] | None = None
    result_code: int | None = None
    rrn: str | None = None
    approval_code: str | None = None
    card_number: str | None = None

    def __post_init__(self):
        data = parse_response(self.message.lower())
        self.result = data.get('result')
        if 'result_code' in data:
            self.result_code = int(data['result_code'])
        self.rrn = data.get('rrn')
        self.approval_code = data.get('approval_code')
        self.card_number = data.get('card_number')


@dataclass
class EndBusinessDayResponse(SuccessResponse):
    result: t.Literal['ok', 'failed'] | None = None
    result_code: int | None = None
    fld_074: str | None = None
    fld_075: str | None = None
    fld_076: str | None = None
    fld_077: str | None = None
    fld_086: str | None = None
    fld_087: str | None = None
    fld_088: str | None = None
    fld_089: str | None = None

    def __post_init__(self):
        data = parse_response(self.message.lower())
        self.result = data.get('result')
        if 'result_code' in data:
            self.result_code = int(data['result_code'])
        self.rrn = data.get('rrn')
        self.approval_code = data.get('approval_code')
        self.card_number = data.get('card_number')


@dataclass
class RecurringResponse(SuccessResponse):
    result: str | None = None
    result_code: str | None = None
    transaction_id: str | None = None
    rrn: str | None = None
    approval_code: str | None = None

    def __post_init__(self):
        data = parse_response(self.message.lower())
        self.result = data.get('result')
        self.result_code = data.get('result_code')
        self.transaction_id = data.get('recurring_transaction_id')
        self.rrn = data.get('recurring_rrn')
        self.approval_code = data.get('approval_code')


@dataclass
class ErrorResponse:
    message: str
    status_code: int
