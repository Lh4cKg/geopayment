import hashlib

from geopayment.providers.utils import gel_to_tetri


def check(password, **params):
    """
    product information transformed to md5, in case of several products
    it should be collected together

    :param password: type of string
    :param params: type of dict
    :return: check

    >>> check
    e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    """

    to_tetri = params.pop('to_tetri', True)
    data = params.pop('products_str', list())
    if not data:
        for p in params['products']:
            if to_tetri is True:
                p['price'] = gel_to_tetri(p['price'])
            data.append(
                f"{p['id']}{p['title']}{p['amount']}{p['price']}{p['type']}"
            )
        data = ''.join(data)

    data = f'{data}{password}'
    return hashlib.md5(data.encode('utf-8')).hexdigest()
