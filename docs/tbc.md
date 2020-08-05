### Documentation for using TBCPay module
There are two types of transaction within this system: SMS and DMS.

SMS - is a direct payment method, money is charged in 1 event, as soon as customer enters the credit card details and clicks proceed.

DMS - is a two step method, first event blocks the money on the card (max 30 days), second event captures the money (second event can be carried out when product is shipped to the customer for example).

Every 24 hours, a merchant must close the business day.

##### Generate Certificate from p12
`p12_to_pem` function return certificate from p12 as pem format. returned certificate
contains cert and cert-key.

```python
from geopayment.crypto import p12_to_pem

cert = '/absolute/path/my_cert.p12'
p12_to_pem(cert=cert, password='cert-pass', file_name='out-cert-name', output='/absolute/output/path/')
# result
'out-cert-name.pem'
'out-cert-name-key.pem'
```

##### Initialize Provider Object
```python
from geopayment import TBCProvider

class MyTBCProvider(TBCProvider):

    @property
    def description(self) -> str:
        """default description"""
        return 'mybrand description'

    @property
    def client_ip(self) -> str:
        return 'xx.xx.xx.xx'

    @property
    def merchant_url(self) -> str:
        return 'https://ecommerce.ufc.ge:18443/ecomm2/MerchantHandler'

    @property
    def cert(self):
        return (
            '/absolute/output/path/out-cert-name.pem',
            '/absolute/output/path/out-cert-name-key.pem'         
        )

```

Consider the first type of authorization (SMS authorization)

1. Generate transaction id

    Function name: `get_trans_id`
    
    input: 
    
        amount: float, int, deciaml (required)
        currency: int, str (required)
        client_ip_addr: str (optional)
        description: str (optional)
        language: str (optional)
    
   ```python
    provider = MyTBCProvider()
    result = provider.get_trans_id(amount=23.50, currency='GEL')
    print(result)
    {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}
    print(provider.trans_id)
    NMQfTRLUTne3eywr9YnAU78Qxxw=
    ```

2. Check transaction status

    Function name: `check_trans_status`
    
    input:
    
        trans_id: str (required) 
        client_ip_addr: str (optional)
    
    
   ```python
    provider = MyTBCProvider()
    result = provider.check_trans_status(trans_id=provider.trans_id)
    print(result)
    {'RESULT': 'OK', 'RESULT_CODE': '000', '3DSECURE': 'ATTEMPTED',
    'CARD_NUMBER': '', 'RRN': '', 'APPROVAL_CODE': ''}
   ```

Consider the type of DMS authorization

1. Generate transaction id with DMS authorization

    Function name: `pre_auth_trans`
  
    input:
    
        amount: float, int, decimal (required)
        currency: int, str (required)
        client_ip_addr: str (optional)
        description: str (optional)
        language: str (optional)
    
    ```python
    provider = MyTBCProvider()
    result = provider.pre_auth_trans(amount=43.20, currency=981)
    print(result)
    {'TRANSACTION_ID': 'NMQfTRLUTne3eywr9YnAU78Qxxw='}
    print(provider.trans_id)
    NMQfTRLUTne3eywr9YnAU78Qxxw=
    ```
2. Commit a transaction generated by DMS authorization

    Function name: `confirm_pre_auth_trans`
    
    input:
    
        trans_id: str (required)
        amount: float, int, decimal (required)
        currency: int, str (required)
        client_ip_addr: str (optional)
        description: str (optional)
        language: str (optional)
        
    ```python
    provider = MyTBCProvider()
    result = provider.confirm_pre_auth_trans(trans_id=provider.trans_id, amount=43.20, currency=981)
    print(result)
    {'RESULT': 'OK', 'RESULT_CODE': '', 'BRN': '' 'APPROVAL_CODE': '', 'CARD_NUMBER': ''}
    ```
   
Consider other operations, e.g. Reversal, Refund, End of Business Day

1. End of Business Day

    Function name: `end_of_business_day`
    ```python
    provider = MyTBCProvider()
    result = provider.end_of_business_day()
    print(result)
    ```
   
2. Transaction reversal
    
    Function name: `reversal_trans`
    
    input:
    
        trans_id: str (required)
        amount: float, int, decimal (required)
        
    ```python
    provider = MyTBCProvider()
    provider.reversal_trans(trans_id=provider.trans_id, amount=12.20)
    {'RESULT': 'OK', 'RESULT_CODE': ''}
    ```

3. Transaction refund

    Function name: `refund_trans`
    
    input:
    
        trans_id: str (required)
        amount: float, int, decimal (required)
        
    ```python
    provider = MyTBCProvider()
    provider.refund_trans(trans_id=provider.trans_id, amount=12.20)
    {'RESULT': '', 'RESULT_CODE': '', 'REFUND_TRANS_ID': ''}
    ```