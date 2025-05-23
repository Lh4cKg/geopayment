import enum


class AuthType(enum.Enum):
    FULL_COMPLETE = 'FULL_COMPLETE'
    PARTIAL_COMPLETE = 'PARTIAL_COMPLETE'
    CANCEL = 'CANCEL'


class Intent(enum.Enum):
    AUTHORIZE = 'AUTHORIZE'
    CAPTURE = 'CAPTURE'


class CapturedMethod(enum.Enum):
    AUTOMATIC = 'AUTOMATIC'
    MANUAL = 'MANUAL'


class ApplicationType(enum.Enum):
    WEB = 'web'
    MOBILE = 'mobile'


class PaymentMethod(enum.Enum):
    CARD = 'card'
    GOOGLE_PAY = 'google_pay'
    APPLE_PAY = 'apple_pay'
    BOG_P2P = 'bog_p2p'
    BOG_LOYALTY = 'bog_loyalty'
    BNPL = 'bnpl'
    BOG_LOAN = 'bog_loan'
    GIFT_CARD = 'gift_card'
