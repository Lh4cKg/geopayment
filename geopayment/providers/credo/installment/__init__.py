import json
import hashlib
from time import time
from typing import Dict, Union

from geopayment.providers.utils import gel_to_tetri
from geopayment.providers.credo.installment.form import InstallmentForm


__all__ = ('Installment',)


class Installment(object):

    @property
    def form(self):
        return InstallmentForm

    def set_installment_data(self, **kwargs) -> Union[str, Dict]:
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
        kwargs['check'] = self.check(**kwargs)
        if 'orderCode' not in kwargs:
            kwargs['orderCode'] = int(time())
        kwargs['installmentLength'] = 1
        kwargs['clientFullName'] = str()
        kwargs['mobile'] = str()
        kwargs['email'] = str()
        kwargs['factAddress'] = str()
        if kwargs.pop('dump', None):
            return json.dumps(kwargs, ensure_ascii=False)
        return kwargs

    def check(self, **params):
        """
        product information transformed to md5, in case of several products
        it should be collected together

        :param password: type of string
        :param params: type of dict
        :return: check

        >>> check
        e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        """

        to_tetri = params.pop('to_tetri', True)
        data = params.pop('products_str', list())
        if not data:
            for p in params['products']:
                if to_tetri is True:
                    p['price'] = gel_to_tetri(p['price'])
                data.append(
                    f"{p['id']}{p['title']}{p['amount']}{p['price']}{p['type']}"
                )
            data = ''.join(data)

        data = f'{data}{self.password}'
        return hashlib.md5(data.encode('utf-8')).hexdigest()
