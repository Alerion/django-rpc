from Cookie import SimpleCookie


class RpcResponse(dict):
    """
    Base class for rpc response clasess
    """
    pass


class Error(RpcResponse):
    """
    Simple responses. Just for pretty code and some kind of "protocol". Example::

        return Error('Something happened', code=error_code, traceback=traceback)
    """
    def __init__(self, text, **kwargs):
        super(Error, self).__init__(error=text, **kwargs)


class Msg(RpcResponse):
    """
    Simple responses. Just for pretty code and some kind of "protocol". Example::

        return Msg('Object saved!')
    """
    def __init__(self, text, **kwargs):
        super(Msg, self).__init__(msg=text, **kwargs)


class RpcHttpResponse(RpcResponse):
    """
    This is vrapper for method's reponse, which allow save some modification of HTTP response.
    For example set COOKIES. This should be flexible and useful for in future.
    """

    def __init__(self, *args, **kwargs):
        super(RpcHttpResponse, self).__init__(*args, **kwargs)
        self.cookies = SimpleCookie()

    def set_cookie(self, key, value='', max_age=None, expires=None, path='/',
                   domain=None, secure=False):
        self.cookies[key] = value
        if max_age is not None:
            self.cookies[key]['max-age'] = max_age
        if expires is not None:
            self.cookies[key]['expires'] = expires
        if path is not None:
            self.cookies[key]['path'] = path
        if domain is not None:
            self.cookies[key]['domain'] = domain
        if secure:
            self.cookies[key]['secure'] = True
