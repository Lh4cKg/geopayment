### Documentation for using iPay (BOG) module


##### Initialize Provider Object
```python
from geopayment import IPayProvider

class MyIPayProvider(IPayProvider):

    @property
    def secret_key(self) -> str:
        # here write client secret key
        return '581ba5eeadd657c8ccddc74c839bd3ad'

    @property
    def client_id(self) -> str:
        # here write client id
        return '1006'

    @property
    def merchant_url(self) -> str:
        return 'https://dev.ipay.ge/opay/api/v1/'

    @property
    def redirect_url(self) -> str:
        return 'http://ebita.ge/success'

```

Consider authorization and checkout orders.

1. Send authorization request 

    Function name: `get_auth`
    
    input: 
    
        grant_type: str (optional), default is `client_credentials`
    
   ```python
    provider = MyIPayProvider()
    provider.get_auth()
    print(provider.access)
    {'access_token': 'eyJraWQiOiIxMDA2IiwiY3R5IjoiYXBwbGljYXRpb25cL2pzb24iLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJQdWJsaWMgcGF5bWVudCBBUEkgVjEiLCJhdWQiOiJpUGF5IERlbW8iLCJpc3MiOiJodHRwczpcL1wvaXBheS5nZSIsImV4cCI6MTU5NjU3Mzg5M30.Iu6CFsbhfQt3hx3n7YEMyrPqQdGol8Is9oT4m1YjY4k', 'token_type': 'Bearer', 'app_id': '1A2019', 'expires_in': 1596573893918}
    ```

2. Checkout orders

    Function name: `checkout`
    
    input:
    
        items: list (required)
        currency_code: str (optional), default is `GEL`
        intent: str (optional) default is `AUTHORIZE`
        shop_order_id: str (optional)
        card_transaction_id: str (optional)
        locale: str (optional)
    
   ```python
    provider = MyIPayProvider()
    result = provider.checkout(items=[
        {'amount': 10.04, 'description': 'product 1', 'quantity': 1, 'product_id': 1},
        {'amount': 5.09, 'description': 'product 2', 'quantity': 1, 'product_id': 2},
    ])
    print(provider.order_status)
    CREATED
    print(provider.rel_approve)
    https://dev.ipay.ge/?order_id=5ead592ae9c19caef0b0e79a066297adf244bed5&locale=ka
    print(result)
    {
       'status': 'CREATED',
       'payment_hash': '1376072fead3a122938390a638a3e9a2377ea879',
       'links': [
           {'href': 'https://dev.ipay.ge/opay/api/v1/checkout/orders/5ead592ae9c19caef0b0e79a066297adf244bed5', 'rel': 'self', 'method': 'GET'},
           {'href': 'https://dev.ipay.ge/?order_id=5ead592ae9c19caef0b0e79a066297adf244bed5&locale=ka', 'rel': 'approve', 'method': 'REDIRECT'}
       ],
       'order_id': '5ead592ae9c19caef0b0e79a066297adf244bed5'
   }
   ```

Consider other operations, e.g. refund, order status, order details, payment details 

1. Transaction refund

    Function name: `refund`
    
    input:
    
        order_id: list (required)
        amount: float, int (required), max decimal places is 2.
        access_token: str (optional)
    
    ```python
    provider = MyIPayProvider()
    result = provider.refund()
    print(result)
    ```
   
2. Order status
    
    Function name: `checkout_status`
    
    input:
    
        order_id: str (required)
        access_token: str (optional)
        
    ```python
    provider = MyIPayProvider()
    result = provider.checkout_status(order_id='5ead592ae9c19caef0b0e79a066297adf244bed5')
    print(result)
    ```

3. Order details

    Function name: `checkout_details`
    
    input:
    
        order_id: str (required)
        access_token: str (optional)
        
    ```python
    provider = MyIPayProvider()
    result = provider.checkout_details(order_id='5ead592ae9c19caef0b0e79a066297adf244bed5')
    print(result)
    ```

4. Payment details

    Function name: `payment_details`
    
    input:
    
        order_id: str (required)
        access_token: str (optional)
        
    ```python
    provider = MyIPayProvider()
    result = provider.payment_details(order_id='5ead592ae9c19caef0b0e79a066297adf244bed5')
    print(result)
    ```
