

def get_client_ip(request) -> str:
    """
    :param request:
    :return: client ip address
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_signature(request) -> str:
    """
    :param request:
    :return: client ip address
    """
    if hasattr(request, 'META'):
        signature = request.META.get('HTTP_CALLBACK_SIGNATURE', '')
    else:
        signature = request.headers.get('Callback-Signature', '')
    return signature
