import json
from time import time
from typing import Dict, Union

from geopayment.providers.credo.installment import Installment


class BaseCredoProvider(object):

    def __init__(self) -> None:
        assert callable(self.merchant_id) is False, \
            '`merchant_id` must be property, not callable'

        assert callable(self.password) is False, \
            '`password` must be property, not callable'

    @property
    def merchant_id(self) -> str:
        """

        :return: merchant id
        """
        raise NotImplementedError(
            'Provider needs implement `merchant_id` function'
        )

    @property
    def password(self) -> str:
        """

        :return: password

        secret string which should be known for only developers of both sides.
        """
        raise NotImplementedError(
            'Provider needs implement `merchant_id` function'
        )


class CredoProvider(Installment, BaseCredoProvider):
    pass
