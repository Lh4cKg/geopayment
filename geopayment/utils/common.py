from __future__ import annotations

import typing as t
from decimal import Decimal


def verify_signature(
        *,
        signature: str,
        request_body: str,
        public_key: str | None = None
):
    # TODO
    if public_key is None:
        public_key = """-----BEGIN PUBLIC KEY-----
            MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu4RUyAw3+CdkS3ZNILQh
            zHI9Hemo+vKB9U2BSabppkKjzjjkf+0Sm76hSMiu/HFtYhqWOESryoCDJoqffY0Q
            1VNt25aTxbj068QNUtnxQ7KQVLA+pG0smf+EBWlS1vBEAFbIas9d8c9b9sSEkTrr
            TYQ90WIM8bGB6S/KLVoT1a7SnzabjoLc5Qf/SLDG5fu8dH8zckyeYKdRKSBJKvhx
            tcBuHV4f7qsynQT+f2UYbESX/TLHwT5qFWZDHZ0YUOUIvb8n7JujVSGZO9/+ll/g
            4ZIWhC1MlJgPObDwRkRd8NFOopgxMcMsDIZIoLbWKhHVq67hdbwpAq9K9WMmEhPn
            PwIDAQAB
            -----END PUBLIC KEY-----""".strip()
    pass


def dict_factory(result: dict) -> t.Dict[str, t.Any]:
    return {
        k: v for k, v in result
        if v is not None and v != {} and v != [] and v != ()
    }


def serialize_dict_factory(result: dict) -> t.Dict[str, t.Any]:
    return {
        k: str(v) if isinstance(v, Decimal) else v for k, v in result
    }


def dropna_serialize_dict_factory(result: dict) -> t.Dict[str, t.Any]:
    return {
        k: str(v) if isinstance(v, Decimal) else v for k, v in result
        if v is not None and v != {} and v != [] and v != ()
    }


def parse_response(content: str) -> t.Dict[str, str]:
    """

    :param content: response from payment provider
    :return: dict

    >>> parse_response('TRANSACTION_ID: Du1eT2N1M4defU743iOpF6G8OYt')
    {'TRANSACTION_ID': 'Du1eT2N1M4defU743iOpF6G8OYt='}
    """

    return dict(
        item.split(': ')
        for item in content.split('\n')
        if item.strip()
    )
