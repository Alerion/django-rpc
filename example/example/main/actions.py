from rpc import RpcRouter, Error, Msg


class MainApiClass(object):

    def hello(self, username):
        return Msg(u'Hello %s' % username)


router = RpcRouter('main:router', {
    'MainApi': MainApiClass(),
})
