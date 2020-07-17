# _*_ coding: utf-8 _*_

"""
Created on Jul 14, 2017

@author: Lasha Gogua
"""

from OpenSSL import crypto


def p12_to_pem(cert=None, password=None, file_name=None, output=str()):
    """
        p12 certificate convert to pem format
    :param cert: Certificate absolute path
    :param password: Certificate passphrase
    :param file_name: Certificate file name
    :param output: Certificate output directory
    :return: certificate and key in pem format
    """

    if not (cert or password):
        cert = input('Enter Certificate absolute path: \n')
        password = input('Enter Certificate passphrase: \n')

    with open(cert, 'rb') as f:
        p12 = crypto.load_pkcs12(f.read(), password)

    dump_cert = crypto.dump_certificate(
        crypto.FILETYPE_PEM, p12.get_certificate()
    )
    dump_key = crypto.dump_privatekey(
        crypto.FILETYPE_PEM, p12.get_privatekey()
    )
    pem_cert = dump_cert + dump_key
    file_name = file_name or p12.get_friendlyname()
    with open(f'{output}{file_name}.pem', 'wb') as pem:
        pem.write(pem_cert)

    with open(f'{output}{file_name}-key.pem', 'wb') as pem_key:
        pem_key.write(dump_key)

    return pem, pem_key
