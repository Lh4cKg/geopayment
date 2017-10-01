# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

import logging
import requests

from ..utils import get_certificate_path, gel_to_tetri
from .. import config as settings

logger = logging.getLogger(__name__)


def generate_transaction_id(amount, currency, client_ip_address, msg_type="SMS", verify=False, module_name='tbc'):
    """

    :param amount: Transaction amount in fractional units
    :param currency: Transaction currency code (ISO 4217)
    :param client_ip_address: Client ip address
    :param msg_type: SMS transaction
    :param verify: Certificate verify
    :param module_name: Payment module
    :return: result

    result -> {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

    TRANSACTION_ID - transaction identifier
    error          - in case of an error

    """

    pay_module = settings.PAYMENT_MODULES.get(module_name)
    payload = {
        "command": "v",
        "amount": gel_to_tetri(amount),
        "currency": currency,
        "client_ip_addr": client_ip_address,
        "language": "ka",
        "description": pay_module['merchant']["Description"],
        "msg_type": msg_type
    }

    logger.info('TBC: Sending Generate Transaction ID %s' % str(payload))

    try:
        response = requests.post(pay_module['merchant_url'], data=payload, verify=verify,
                                 cert=(get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['MerchantName']),
                                       get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['KeyFile'])
                                       )
                                 )
        if response.status_code == 200:
            result = dict(item.split(": ") for item in response.text.split("\n") if item.strip() != '')
        else:
            result = {
                'RESULT': 'ERROR',
                'STATUS_CODE': response.status_code,
            }
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = {
            'RESULT': 'ERROR',
            'ERROR_TYPE': 'TIMEOUT',
        }

    logger.info('TBC: Received Generated Transaction ID result %s' % (str(result)))

    return result


def check_transaction_status(trans_id, client_ip_address, verify=False, module_name='tbc'):
    """

    :param trans_id: Transaction identifier
    :param client_ip_address: Client ip address
    :param verify: Certificate verify
    :param module_name: payment module
    :return: result

    result -> {'RESULT': 'OK', 'RESULT_CODE': '000', '3DSECURE': 'ATTEMPTED',
               'CARD_NUMBER': '', 'RRN': '', 'APPROVAL_CODE': ''}

    RESULT             - transaction status
    RESULT_CODE        - transaction result code
    3DSECURE           - 3D Secure authorization
    RRN                - retrieval reference number
    APPROVAL_CODE      - approval code
    CARD_NUMBER        - masked card number
    error              - in case of an error
    warning            - in case of warning

    """

    payload = {
        "command": "c",
        "trans_id": trans_id,
        "client_ip_addr": client_ip_address,
    }
    pay_module = settings.PAYMENT_MODULES.get(module_name)

    logger.info('TBC: Sending Check %s for trans id %s' % (str(payload), trans_id))

    try:
        response = requests.post(pay_module['merchant_url'], data=payload, verify=verify,
                                 cert=(get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['MerchantName']),
                                       get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['KeyFile'])
                                       )
                                 )
        if response.status_code == 200:
            result = dict(item.split(": ") for item in response.text.split("\n") if item.strip() != '')
        else:
            result = {
                'RESULT': 'ERROR',
                'STATUS_CODE': response.status_code,
            }
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = {
            'RESULT': 'ERROR',
            'ERROR_TYPE': 'TIMEOUT',
        }

    logger.info('TBC: Received Check result %s for transaction %s' % (str(result), trans_id))

    return result


def reversal_transaction(trans_id, amount, verify=False, module_name='tbc'):
    """

    :param trans_id: Transaction identifier
    :param amount: Transaction amount in fractional units
    :param verify: Certificate verify
    :param module_name: Payment module
    :return: result

    result -> {'RESULT': 'OK', 'RESULT_CODE': ''}

    RESULT         - reversal transaction status
    RESULT_CODE    - reversal result code
    error          - in case of an error
    warning        - in case of warning

    """

    payload = {
        "command": "r",
        "trans_id": trans_id,
        "amount": gel_to_tetri(amount),
    }
    pay_module = settings.PAYMENT_MODULES.get(module_name)

    logger.info('TBC: Sending Reversal %s for trans id %s' % (str(payload), trans_id))

    try:
        response = requests.post(pay_module['merchant_url'], data=payload, verify=verify,
                                 cert=(get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['MerchantName']),
                                       get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['KeyFile'])
                                       )
                                 )
        if response.status_code == 200:
            result = dict(item.split(": ") for item in response.text.split("\n") if item.strip() != '')
        else:
            result = {
                'RESULT': 'ERROR',
                'STATUS_CODE': response.status_code,
            }
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = {
            'RESULT': 'ERROR',
            'ERROR_TYPE': 'TIMEOUT',
        }

    logger.info('TBC: Received Reversal result %s for transaction %s' % (str(result), trans_id))

    return result


def refund_transaction(trans_id, amount, verify=False, module_name='tbc'):
    """

    :param trans_id: Transaction identifier
    :param amount: Payment module
    :param verify: Certificate verify
    :param module_name: Transaction amount in fractional units
    :return: result

    result -> {'RESULT': '', 'RESULT_CODE': '', 'REFUND_TRANS_ID': ''}

    RESULT              - refund transaction status
    RESULT_CODE         - refund result code
    REFUND_TRANS_ID     - refund transaction identifier
    error               - in case of an error
    warning             - in case of warning

    """

    payload = {
        "command": "k",
        "trans_id": trans_id,
        "amount": gel_to_tetri(amount),
    }

    pay_module = settings.PAYMENT_MODULES.get(module_name)

    logger.info('TBC: Sending Refund %s for trans id %s' % (str(payload), trans_id))

    try:
        response = requests.post(pay_module['merchant_url'], data=payload, verify=verify,
                                 cert=(get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['MerchantName']),
                                       get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['KeyFile'])
                                       )
                                 )
        if response.status_code == 200:
            result = dict(item.split(": ") for item in response.text.split("\n") if item.strip() != '')
        else:
            result = {
                'RESULT': 'ERROR',
                'STATUS_CODE': response.status_code,
            }
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = {
            'RESULT': 'ERROR',
            'ERROR_TYPE': 'TIMEOUT',
        }

    logger.info('TBC: Received Refund result %s for transaction %s' % (str(result), trans_id))

    return result


def dms_authorization(amount, currency, client_ip_address, msg_type="DMS", verify=False, module_name='tbc'):
    """

    :param amount: Transaction amount in fractional units
    :param currency: Transaction currency code (ISO 4217)
    :param client_ip_address: Client ip address
    :param msg_type: DMS authorization
    :param verify: Certificate verify
    :param module_name: Payment module
    :return: result

     result -> {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}

    TRANSACTION_ID  - transaction identifier
    error           - in case of an error

    """

    pay_module = settings.PAYMENT_MODULES.get(module_name)
    payload = {
        "command": "a",
        "amount": gel_to_tetri(amount),
        "currency": currency,
        "client_ip_addr": client_ip_address,
        "language": "ka",
        "description": pay_module['merchant']["Description"],
        "msg_type": msg_type
    }

    logger.info('TBC: Sending DMS Transaction %s' % str(payload))

    try:
        response = requests.post(pay_module['merchant_url'], data=payload, verify=verify,
                                 cert=(get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['MerchantName']),
                                       get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['KeyFile'])
                                       )
                                 )
        if response.status_code == 200:
            result = dict(item.split(": ") for item in response.text.split("\n") if item.strip() != '')
        else:
            result = {
                'RESULT': 'ERROR',
                'STATUS_CODE': response.status_code,
            }
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = {
            'RESULT': 'ERROR',
            'ERROR_TYPE': 'TIMEOUT',
        }

    logger.info('TBC: Received DMS Transaction result %s' % (str(result)))

    return result


def confirm_dms_transaction(trans_id, amount, currency, client_ip_address, msg_type="DMS", verify=False, module_name='tbc'):
    """

    :param trans_id: Transaction identifier
    :param amount: Transaction amount in fractional units
    :param currency: Transaction currency code (ISO 4217)
    :param client_ip_address: Client ip address
    :param msg_type: DMS transaction
    :param verify: Certificate verify
    :param module_name: Payment module
    :return: result

    result -> {'RESULT': 'OK', 'RESULT_CODE': '', 'BRN': '' 'APPROVAL_CODE': '', 'CARD_NUMBER': ''}

    RESULT          - DMS transaction status
    RESULT_CODE     - DMS transaction result code
    BRN             - retrieval reference number
    APPROVAL_CODE   - approval code
    CARD_NUMBER     - masked card number
    error           - in case of an error

    """

    pay_module = settings.PAYMENT_MODULES.get(module_name)
    payload = {
        "command": "t",
        "trans_id": trans_id,
        "amount": gel_to_tetri(amount),
        "currency": currency,
        "client_ip_addr": client_ip_address,
        "description": pay_module['merchant']["Description"],
        "language": "ka",
        "msg_type": msg_type
    }

    logger.info('TBC: Sending Completion %s for trans id %s' % (str(payload), trans_id))
    try:
        response = requests.post(pay_module['merchant_url'], data=payload, verify=verify,
                                 cert=(get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['MerchantName']),
                                       get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['KeyFile'])
                                       )
                                 )
        if response.status_code == 200:
            result = dict(item.split(": ") for item in response.text.split("\n") if item.strip() != '')
        else:
            result = {
                'RESULT': 'ERROR',
                'STATUS_CODE': response.status_code,
            }
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = {
            'RESULT': 'ERROR',
            'ERROR_TYPE': 'TIMEOUT',
        }

    logger.info('TBC: Received Completion result %s for transaction %s' % (str(result), trans_id))

    return result


def end_of_business_day(verify=False, module_name='tbc'):
    """

    :param verify: Certificate verify
    :param module_name: Payment module
    :return: result

    result -> {'RESULT': '', 'RESULT_CODE': '', 'FLD_075': ''}

    RESULT          - end of business day status
    RESULT_CODE     - end-of-business-day result code

    """

    payload = {
        "command": "b",
    }
    pay_module = settings.PAYMENT_MODULES.get(module_name)

    logger.info('TBC: Sending End Of Business Day %s' % (str(payload)))

    try:
        response = requests.post(pay_module['merchant_url'], data=payload, verify=verify,
                                 cert=(get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['MerchantName']),
                                       get_certificate_path(pay_module['module_name'],
                                                            pay_module['merchant']['KeyFile'])
                                       )
                                 )
        if response.status_code == 200:
            result = dict(item.split(": ") for item in response.text.split("\n") if item.strip() != '')
        else:
            result = {
                'RESULT': 'ERROR',
                'STATUS_CODE': response.status_code,
            }
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        result = {
            "RESULT": "ERROR",
            "ERROR_TYPE": "TIMEOUT",
        }

    logger.info('TBC: Received End Of Business Day result %s' % str(result))

    return result
