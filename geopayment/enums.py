import enum


class Currency(enum.Enum):
    GEL: int = 981
    USD: int = 840
    EUR: int = 978
    GBP: int = 826

    @classmethod
    def allowed_currencies(cls):
        return cls._member_map_


class AuthType(enum.Enum):
    FULL_COMPLETE: str = 'FULL_COMPLETE'
    PARTIAL_COMPLETE: str = 'PARTIAL_COMPLETE'
    CANCEL: str = 'CANCEL'


class Intent(enum.Enum):
    AUTHORIZE: str = 'AUTHORIZE'
    CAPTURE: str = 'CAPTURE'


class CapturedMethod(enum.Enum):
    AUTOMATIC: str = 'AUTOMATIC'
    MANUAL: str = 'MANUAL'


class Language(enum.Enum):
    KA: str = 'ka'
    EN_US: str = 'en-US'
