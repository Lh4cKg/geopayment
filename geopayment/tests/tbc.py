import unittest

from geopayment import TBCProvider


class TestsTBCProvider(unittest.TestCase):

    def setUp(self):

        class MyTBCProvider(TBCProvider):

            @property
            def description(self):
                return 'mybrand description'

            @property
            def client_ip(self):
                return '127.0.0.1'

            @property
            def service_url(self):
                return 'https://ecommerce.ufc.ge:18443/ecomm2/MerchantHandler'

            @property
            def cert(self):
                return (
                    '/absolute/output/path/out-cert-name.pem',
                    '/absolute/output/path/out-cert-name-key.pem'
                )

        self.provider = MyTBCProvider()

    def test_description(self):
        self.assertIs(
            type(self.provider.description), str,
            '`description` must be string'
        )

    def test_client_ip(self):
        self.assertIs(
            type(self.provider.client_ip), str,
            '`client_ip` must be string'
        )
        self.assertRegex(
            self.provider.client_ip,
            r'^\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b$',
            '`client_ip` is incorrect'
        )

    def test_service_url(self):
        self.assertIs(
            type(self.provider.service_url), str,
            '`service_url` must be string'
        )
        self.assertRegex(
            self.provider.service_url,
            r'^(https|http):\/\/.*\.[a-z]{2,6}',
            '`service_url` is incorrect'
        )

    def test_cert(self):
        self.assertIs(
            type(self.provider.cert), tuple,
            '`service_url` must be tuple'
        )
        self.assertIs(
            type(self.provider.cert[0]), str,
            '`cert` must be string'
        )
        self.assertIs(
            type(self.provider.cert[1]), str,
            '`cert key` must be string'
        )

    def test_get_trans_id(self):
        result = self.provider.get_trans_id(amount=23.50, currency='GEL')
        self.assertIsNone(
            self.provider.trans_id,
            'transaction identificator is none'
        )
        self.assertIs(
            type(self.provider.trans_id), str,
            '`trans_id` must be string'
        )
        self.assertNotIn(
            'TRANSACTION_ID', result,
            '`result` not contains transaction identificator'
        )

    def test_pre_auth_trans(self):
        result = self.provider.pre_auth_trans(amount=23.50, currency=981)
        self.assertIsNone(
            self.provider.trans_id,
            'transaction identificator is none'
        )
        self.assertIs(
            type(self.provider.trans_id), str,
            '`trans_id` must be string'
        )
        self.assertNotIn(
            'TRANSACTION_ID', result,
            '`result` not contains transaction identificator'
        )

    def test_confirm_pre_auth_trans(self):
        self.assertIsNone(
            self.provider.trans_id,
            'transaction identificator is none'
        )
        self.assertIs(
            type(self.provider.trans_id), str,
            '`trans_id` must be string'
        )
        result = self.provider.confirm_pre_auth_trans(
            amount=23.50, currency=981
        )
        self.assertNotIn(
            'RESULT', result,
            '`result` not contains DMS transaction status'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not contains DMS transaction result '
            'code (success, fail, etc)'
        )
        self.assertNotIn(
            'APPROVAL_CODE', result,
            '`result` not contains DMS transaction approval code'
        )
        self.assertNotIn(
            'BRN', result,
            '`result` not contains DMS transaction retrieval reference number'
        )

    def test_check_trans_status(self):
        self.assertIsNone(
            self.provider.trans_id,
            'transaction identificator is none'
        )
        self.assertIs(
            type(self.provider.trans_id), str,
            '`trans_id` must be string'
        )
        result = self.provider.check_trans_status(
            trans_id=self.provider.trans_id
        )
        self.assertNotIn(
            'RESULT', result,
            '`result` not contains transaction status'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not contains transaction result '
            'code (success, fail, etc)'
        )

    def test_reversal_trans(self):
        self.assertIsNone(
            self.provider.trans_id,
            'transaction identificator is none'
        )
        self.assertIs(
            type(self.provider.trans_id), str,
            '`trans_id` must be string'
        )
        result = self.provider.check_trans_status(
            trans_id=self.provider.trans_id,
            amount=10.12
        )
        self.assertNotIn(
            'RESULT', result,
            '`result` not contains reversal transaction status'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not contains reversal transaction result '
            'code (success, fail, etc)'
        )

    def test_refund_trans(self):
        self.assertIsNone(
            self.provider.trans_id,
            'transaction identificator is none'
        )
        self.assertIs(
            type(self.provider.trans_id), str,
            '`trans_id` must be string'
        )
        result = self.provider.check_trans_status(
            trans_id=self.provider.trans_id,
            amount=10.12
        )
        self.assertNotIn(
            'RESULT', result,
            '`result` not contains refund transaction status'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not contains refund transaction result '
            'code (success, fail, etc)'
        )
        self.assertNotIn(
            'REFUND_TRANS_ID', result,
            '`result` not contains refund transaction identificator'
        )

    def test_card_register_with_deduction(self):

        result = self.provider.card_register_with_deduction(
            amount=20.3, currency='GEL', biller_client_id='GEOpayMENTs',
            expiry='1225', perspayee_expiry='1225', perspayee_gen=1
        )
        self.assertNotIn(
            'HTTP_STATUS_CODE', result,
            '`result` not includes `HTTP_STATUS_CODE`'
        )
        self.assertNotIn(
            'RESULT', result,
            'not includes `RESULT`'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not includes `RESULT_CODE` (success, fail, etc)'
        )

    def test_card_register_with_zero_auth(self):
        result = self.provider.card_register_with_zero_auth(
            currency='GEL', biller_client_id='GEOpayMENTs', expiry='1225'
        )
        self.assertNotIn(
            'HTTP_STATUS_CODE', result,
            '`result` not includes `HTTP_STATUS_CODE`'
        )
        self.assertNotIn(
            'RESULT', result,
            'not includes `RESULT`'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not includes `RESULT_CODE` (success, fail, etc)'
        )

    def test_recurring_payment(self):
        result = self.provider.recurring_payment(
            amount=20.3, currency='GEL', biller_client_id='GEOpayMENTs'
        )
        self.assertNotIn(
            'HTTP_STATUS_CODE', result,
            '`result` not includes `HTTP_STATUS_CODE`'
        )
        self.assertNotIn(
            'RESULT', result,
            'not includes `RESULT`'
        )
        self.assertNotIn(
            'TRANSACTION_ID', result,
            '`result` not includes `TRANSACTION_ID`'
        )
        self.assertNotIn(
            'APPROVAL_CODE', result,
            '`result` not includes `APPROVAL_CODE`'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not includes `RESULT_CODE` (success, fail, etc)'
        )

    def test_refund_to_debit_card(self):
        pass

    def test_end_of_business_day(self):
        result = self.provider.end_of_business_day()

        self.assertNotIn(
            'RESULT', result,
            '`result` not contains end of business day status'
        )
        self.assertNotIn(
            'RESULT_CODE', result,
            '`result` not contains end of business day status '
            'code (success, fail, etc)'
        )
        self.assertNotIn(
            'FLD_075', result,
            '`result` not contains number of credit reversals'
        )
        self.assertNotIn(
            'FLD_076', result,
            '`result` not contains number of debit transactions'
        )
        self.assertNotIn(
            'FLD_087', result,
            '`result` not contains amount of credit reversals'
        )
        self.assertNotIn(
            'FLD_088', result,
            '`result` not contains amount of debit transactions'
        )


if __name__ == '__main__':
    unittest.main()
