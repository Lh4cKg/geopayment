from base64 import b64encode
from dataclasses import dataclass
from typing import Optional, Any, Dict

from geopayment.providers.utils import tbc_installment_params, _request


@dataclass
class AuthData:
    access_token: str
    token_type: str
    scope: str
    issued_at: str
    expires_in: int
    HTTP_STATUS_CODE: int


class BaseInstallmentProvider(object):
    auth: AuthData = None
    session_id: str = None
    redirect_url: str = None
    http_status_code: str = None

    def __init__(self) -> None:
        assert callable(self.merchant_key) is False, \
            '`merchant_key` must be property, not callable'
        assert callable(self.campaign_id) is False, \
            '`campaign_id` must be property, not callable'
        assert callable(self.key) is False, \
            '`key` must be property, not callable'
        assert callable(self.secret) is False, \
            '`secret` must be property, not callable'
        assert callable(self.service_url) is False, \
            '`service_url` must be property, not callable'
        assert callable(self.version) is False, \
            '`version` must be property, not callable'

    @property
    def merchant_key(self):
        """

        :return: merchant key
        """
        raise NotImplementedError(
            'Provider needs implement `merchant_key` function'
        )

    @property
    def campaign_id(self):
        """

        :return: campaign id
        """
        raise NotImplementedError(
            'Provider needs implement `campaign_id` function'
        )

    @property
    def key(self):
        """

        :return: merchant apiKey
        """
        raise NotImplementedError(
            'Provider needs implement api `key` function'
        )

    @property
    def secret(self):
        """

        :return: merchant apiSecret
        """
        raise NotImplementedError(
            'Provider needs implement api `secret` function'
        )

    @property
    def service_url(self) -> str:
        """

        :return: installment service url
        """
        raise NotImplementedError(
            'Provider needs implement installment `service_url` function'
        )

    def __str__(self):
        return (
            f'{self.__class__.__name__}('
            f'merchant_key={self.merchant_key}, '
            f'campaign_id={self.campaign_id}, '
            f'key={self.key}, '
            f'secret={self.secret}'
            f')'
        )

    def get_basic_auth(self) -> bytes:
        return b64encode(f'{self.key}:{self.secret}'.encode())

    @property
    def url(self):
        service_url = self.service_url
        if not service_url.endswith('/'):
            service_url = f'{service_url}/'
        return service_url


class TBCInstallmentProvider(BaseInstallmentProvider):

    @tbc_installment_params(
        endpoint='oauth/token', api='auth',
        grant_type='client_credentials', scope='online_installments'
    )
    @_request(verify=True, timeout=(3, 10), method='post')
    def auth(self, **kwargs: Optional[Any]) -> AuthData:
        """
        api doc <https://developers.tbcbank.ge/docs/installment-get-access-token>
        grant_type: grant_type for oauth client credentials flow
        scope: oauth scope

        :param kwargs: Other endpoint parameters
        :return: AuthData

        >>> provider = MyTBCInstallmentProvider()
        >>> provider.get_auth()
        AuthData(
            access_token='BqicqA8j6mM84He7pf0NOrGIHWUK',
            token_type='Bearer',
            scope='online_installments',
            issued_at='1671844817741',
            expires_in=7775999,
            HTTP_STATUS_CODE=200
        )


        access_token     - Access token. Used to access resources protected by oauth.
                            The token is reference token.
        token_type       - Token type. Currently only BearerToken is supported.
        scope            - Scope for which access token was issued for.
        issued_at        - Unix timestamp access token was issued at.
        expires_in       - Milliseconds, access token will expire.
        HTTP_STATUS_CODE - HTTP response status codes indicate whether a specific
                            HTTP request has been successfully completed.

        """

        self.http_status_code = kwargs['http_status_code']
        result = kwargs['result']
        if 'fault' in result:
            return result
        self.auth = AuthData(**result)
        return self.auth

    @tbc_installment_params(
        endpoint='v1/online-installments/applications', api='create',
    )
    @_request(verify=True, timeout=(3, 10), method='post')
    def create(self,  **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        [api doc](https://developers.tbcbank.ge/docs/installment-initiate-online-installment-application)

        merchant_key: (required)	string   -	merchant unique identifier in online installments module

        campaign_id:	string	-  online installments campaign id

        invoice_id:	string   -	invoice id

        products: (required)  -  list of installment products
            - name:	string   -	product description
            - price: (required)	number (decimal)  -   product price in Georgian Lari format: 0.00
            - quantity: (required)	integer (int32)  -	number of purchased units

        :param kwargs: Other endpoint parameters
        :return: Dict - response contains location header with correspondins
                 redirect URL and unique sessionId of the initiated application.

        >>> provider = MyTBCInstallmentProvider()
        >>> provider.create()
        {
            'session_id': 'e4ff7785-0be7-46f7-aca7-12691a521091',
            'redirect_url': 'https://tbcinstallmenttst.tbcbank.ge/Installment/InitializeNewLoan?sessionId=e4ff7785-0be7-46f7-aca7-12691a521091'
        }


        session_id: guid   -  unique identifier of the online application session.
                              should be saved for follow-up application requests (e.g. confirm application).
        redirect_url: string (uri)   -	URI where the client should be redirected to continue Installment Loan appication.
        HTTP_STATUS_CODE - HTTP response status codes indicate whether a specific
                            HTTP request has been successfully completed.

        """

        self.http_status_code = kwargs['http_status_code']
        self.session_id = kwargs['result'].get('sessionId')
        self.redirect_url = kwargs['headers'].get('location')
        if self.session_id and self.redirect_url:
            return {
                'session_id': self.session_id, 'redirect_url': self.redirect_url
            }
        return kwargs['result']

    @tbc_installment_params(
        endpoint='v1/online-installments/applications/{session_id}/confirm',
        api='confirm',
    )
    @_request(verify=True, timeout=(3, 10), method='post')
    def confirm(self,  **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        [api doc](https://developers.tbcbank.ge/docs/installment-confirm-application)

        merchant_key: (required)  string   -	merchant unique identifier in online installments module

        session_id:	guid   -  unique session Id of initiated application

        :param kwargs: Other endpoint parameters
        :return: Dict - In case of a successful response, 200 OK will be returned.
                the body will contain "id": null which indicates that no errors occurred.

        >>> provider = MyTBCInstallmentProvider()
        >>> provider.confirm()
        {'HTTP_STATUS_CODE': 200}

        HTTP_STATUS_CODE - HTTP response status codes indicate whether a specific
                            HTTP request has been successfully completed.

        """

        self.http_status_code = kwargs['http_status_code']
        return kwargs['result']

    @tbc_installment_params(
        endpoint='v1/online-installments/applications/{session_id}/cancel',
        api='cancel',
    )
    @_request(verify=True, timeout=(3, 10), method='post')
    def cancel(self,  **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        [api doc](https://developers.tbcbank.ge/docs/installment-cancel-application)

        merchant_key: (required)  string   -	merchant unique identifier in online installments module

        session_id:	guid   -  unique session Id of initiated application

        :param kwargs: Other endpoint parameters
        :return: Dict - In case of a successful response, 200 OK will be returned.
                the body will contain "id": null which indicates that no errors occurred.

        >>> provider = MyTBCInstallmentProvider()
        >>> provider.cancel()
        {'HTTP_STATUS_CODE': 200}

        HTTP_STATUS_CODE - HTTP response status codes indicate whether a specific
                            HTTP request has been successfully completed.

        """
        self.http_status_code = kwargs['http_status_code']
        return kwargs['result']

    @tbc_installment_params(
        endpoint='v1/online-installments/applications/{session_id}/status',
        api='status',
    )
    @_request(verify=True, timeout=(3, 10), method='post')
    def status(self,  **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        [api doc](https://developers.tbcbank.ge/docs/installment-get-application-status)

        merchant_key: (required)  string   -	merchant unique identifier in online installments module

        session_id:	guid   -  unique session Id of initiated application

        :param kwargs: Other endpoint parameters
        :return: Dict - In case of a successful response, 200 OK will be returned.
                the body will contain "amount", "statusId", "contributionAmount", "description"
                 which indicates that no errors occurred.

        >>> provider = MyTBCInstallmentProvider()
        >>> provider.status()
        {
            "amount": 150.33,
            "contributionAmount": null,
            "statusId": 9,
            "description": "Installment pending Disbursed (Confirmed from both side)"
        }

        amount:	number (decimal) -	total amount of installment format: 0.00
        contributionAmount:	number (decimal)  - contribution amount
        statusId: integer  -   id of possible status in range of 0-9
        description: string	 -  description of possible status
        HTTP_STATUS_CODE - HTTP response status codes indicate whether a specific
                            HTTP request has been successfully completed.

        """
        self.http_status_code = kwargs['http_status_code']
        return kwargs['result']

    @tbc_installment_params(
        endpoint='v1/online-installments/merchant/applications/status-changes',
        api='statuses',
    )
    @_request(verify=True, timeout=(3, 10), method='post')
    def statuses(self,  **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        [api doc](https://developers.tbcbank.ge/docs/installment-merchant-application-statuses)

        merchant_key: (required)  string   -	merchant unique identifier in online installments module

        take: integer  -	maximum number of changed statuses to be returned with one request

        :param kwargs: Other endpoint parameters
        :return: Dict

        >>> provider = MyTBCInstallmentProvider()
        >>> provider.statuses()
        {
            "amount": 150.33,
            "contributionAmount": null,
            "statusId": 9,
            "description": "Installment pending Disbursed (Confirmed from both side)"
        }

        synchronizationRequestId: string  -   unique identified of request
        totalCount:	number  -	total amount of changed statuses
        statusChanges: array -	list of applications with changed statuses
        HTTP_STATUS_CODE - HTTP response status codes indicate whether a specific
                            HTTP request has been successfully completed.

        """
        self.http_status_code = kwargs['http_status_code']
        return kwargs['result']

    @tbc_installment_params(
        endpoint='v1/online-installments/merchant/applications/status-changes-sync',
        api='status-sync',
    )
    @_request(verify=True, timeout=(3, 10), method='post')
    def status_sync(self,  **kwargs: Optional[Any]) -> Dict[str, str]:
        """
        [api doc](https://developers.tbcbank.ge/docs/installment-merchant-application-status-sync)

        merchant_key: (required)  string   -	merchant unique identifier in online installments module

        synchronizationRequestId: string  -   unique identified of request

        :param kwargs: Other endpoint parameters
        :return: Dict - In case of successful synchronization, 200 OK will be returned.

        >>> provider = MyTBCInstallmentProvider()
        >>> provider.status_sync()
        {}

        HTTP_STATUS_CODE - HTTP response status codes indicate whether a specific
                            HTTP request has been successfully completed.

        """
        self.http_status_code = kwargs['http_status_code']
        return kwargs['result']
