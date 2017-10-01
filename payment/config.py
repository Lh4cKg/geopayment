# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

from collections import OrderedDict


PAYMENT_MODULES = OrderedDict(
    {
        "tbc":
            {
                "display_name": "თიბისი",
                "payment_type": "plastic_card",
                "module_name": "tbc",
                "image": "tbc.jpg",
                "min_limit": 1,
                "max_limit": 1000,
                "ufc_merchant_key": "TbcMerchant",
                "merchant_url": "https://securepay.ufc.ge:18443/ecomm2/MerchantHandler",
                "customer_url": "https://securepay.ufc.ge/ecomm2/ClientHandler",
                "merchant": {
                    "MerchantName": "მერჩანტის უნიკალური იდენტიფიკატორი",
                    "Currency": "981",
                    "Password": "მერჩანტის პაროლი",
                    "KeyFile": "სერტიფიკატის პაროლის ფაილის სახელი, მაგ. 0000000-Key",
                    "Description": "აღწერა",
                },
                "is_testing": True,
            },
    },
)


# currency codes (ISO 4217)
# https://en.wikipedia.org/wiki/ISO_4217

CURRENCY_CODES = OrderedDict(
    {
        'GEL': 981,
        'USD': 840,
        'EUR': 978,
    }
)
