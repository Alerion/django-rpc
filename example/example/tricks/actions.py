from rpc import RpcRouter, Error, Msg


class TricksApiClass(object):

    def func1(self, user, request):
        return Msg(u'func1')


class TricksOneApiClass(object):

    def func2(self, val, **kwargs):
        return Msg(u'func2')


class CustomRouter(RpcRouter):

    def extra_kwargs(self, request, *args, **kwargs):
        print args, kwargs
        return {
            'request': request,
            'user': request.user
        }


custom_router = CustomRouter('tricks:custom_router', {
    'TricksApi': TricksApiClass(),
    'TricksOneApi': TricksOneApiClass()
})
