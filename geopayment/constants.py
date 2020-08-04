# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

# currency codes (ISO 4217)
# https://en.wikipedia.org/wiki/ISO_4217

CURRENCY_SYMBOLS = ('GEL', 'USD', 'EUR')
CURRENCY_CODES = (981, 840, 978)

ALLOW_CURRENCY_CODES = dict(zip(CURRENCY_SYMBOLS, CURRENCY_CODES))

DEFAULT_PAYLOAD_ARGS = ('command', 'msg_type')

BOG_ITEM_KEYS = ('amount', 'description', 'quantity', 'product_id')
