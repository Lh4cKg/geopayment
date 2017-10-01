# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

import os

from decimal import Decimal
from django.conf import settings
from .config import CURRENCY_CODES


def get_client_ip(request):
    """

    :param request:
    :return: client ip address
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_certificate_path(provider, cert):
    """

    :param provider:
    :param cert: Certificate absolute path
    :return: certificate
    """

    certificate = os.path.join(settings.BASE_DIR, '../payment/%s/certificates/%s.pem' % (provider, cert))
    return certificate


def gel_to_tetri(amount):
    """

    :param amount: type of decimal
    :return: amount in tetri
    """
    return int(Decimal(amount).quantize(Decimal('1.00')) * 100)


def get_currency_code(code):
    """

    :param code: currency code
    :return: currency code
    """

    return CURRENCY_CODES.get(code)
