from typing import Optional, Any, Dict

from geopayment.providers.bog.provider import IPayProvider
from geopayment.providers.utils import _request, bog_params


class IPayInstallmentProvider(IPayProvider):
    default_locale = 'ka'

    @bog_params(currency_code='GEL', endpoint='installment/checkout', api='installment-checkout')
    @_request(verify=True, timeout=(3, 10), method='post')
    def checkout(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        installment checkout api docs: https://api.bog.ge/docs/installment/create-order
        :param kwargs:
        :return:
        """

        result = kwargs['result']
        if 'status' in result:
            self.order_status = result['status']
        if 'links' in result and self.order_status:
            link = list(
                filter(lambda x: x['rel'] == 'target', result['links'])
            )
            if link:
                self.rel_approve = link[0]['href']
        return result

    @bog_params(currency_code='GEL', endpoint='services/installment/calculate', api='installment-calculate')
    @_request(verify=True, timeout=(3, 10), method='post')
    def calculate(self, **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        installment calculate api docs: https://api.bog.ge/docs/installment/get-discounts
        :param kwargs:
        :return:
        """

        result = kwargs['result']
        if 'discounts' in result:
            return result['discounts']
        return result
