import enum


class CommandType(enum.Enum):
    CREATE = 'v'
    STATUS = 'c'
    REVERSAL = 'r'
    REFUND = 'k'
    PRE_AUTH = 'a'
    PRE_AUTH_CONFIRM = 't'
    PRE_AUTH_CARD_REGISTER_CONFIRM = 'd'
    CARD_REGISTER = 'p'
    CARD_REGISTER_CONFIRM = 'z'
    RECURRING = 'e'
    PRE_AUTH_RECURRING = 'f'
    REFUND_TO_DEBIT_CARD = 'g'
    END_BUSINESS_DAY = 'b'


class MessageType(enum.Enum):
    SMS = 'SMS'
    DMS = 'DMS'
    AUTH = 'AUTH'


class Language(enum.Enum):
    KA = 'ka'
    EN = 'en'
