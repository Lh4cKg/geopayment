import enum


class Language(enum.Enum):
    KA = 'ka'
    EN_US = 'en-US'
    EN = 'en'
    GE = 'ge'


class Currency(enum.IntEnum):
    GEL = 981
    USD = 840
    EUR = 978
    GBP = 826

    @classmethod
    def available(cls):
        return cls._member_map_
