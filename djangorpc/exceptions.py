class BaseRpcException(Exception):
    """
    Base exception.
    """
    pass


class RpcExceptionEvent(BaseRpcException):
    """
    This exception is sent to server as Ext.Direct.ExceptionEvent.
    So we can handle it in client and show pretty message for user.
    Example::

        class MainApiClass(object):

            def func2(self, user):
                if not user.is_authenticated():
                    raise RpcExceptionEvent(u'Permission denied.')

    And you can catch this with::

        jQuery.Rpc.on('exception', function(event){
            alert('ERROR: '+event.message);
        });
    """
    pass
