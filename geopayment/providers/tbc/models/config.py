from __future__ import annotations

import re
import typing as t
from pydantic import Field
from pydantic.dataclasses import dataclass


__all__ = ['TBCPayConfig']


API_URL_NORMALIZE_REGEX = re.compile(r'((/(v1|v1/))|/)$')
API_VERSION_NORMALIZE_REGEX = re.compile(r'/')



@dataclass
class TBCPayConfig:
    client_ip: str
    description: str
    cert: tuple[str, str]
    verbose: bool = False
    service_url: str = 'https://ecommerce.ufc.ge:18443/ecomm2/MerchantHandler'
