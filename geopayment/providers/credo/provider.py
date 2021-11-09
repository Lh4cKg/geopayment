from time import time
from typing import Dict

from geopayment.providers.credo.installment import check


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


class CredoProvider(BaseCredoProvider):

    def installment(self, **kwargs) -> Dict:
        """
        {
          "merchantId": "7220",
          "orderCode": "17407",
          "check": "f61136837ebe753b4a1e9b9f9893f805",
          "products": [
            {
              "id": "4634",
              "title": "PHILIPS HP6549/00",
              "amount": "2",
              "price": "41400",
              "type": "0"
            }
          ],
          "installmentLength": 12,
          "clientFullName": "სახელი, გვარი",
          "mobile": "595123456",
          "email": "info@credo.ge",
          "factAddress": "test address N6"
        }

        """

        kwargs['merchantId'] = self.merchant_id
        kwargs['check'] = check(self.password, **kwargs)
        if 'orderCode' not in kwargs:
            kwargs['orderCode'] = int(time())
        kwargs['installmentLength'] = 1
        kwargs['clientFullName'] = str()
        kwargs['mobile'] = str()
        kwargs['email'] = str()
        kwargs['factAddress'] = str()
        return kwargs
