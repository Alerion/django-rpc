from __future__ import unicode_literals

from djangorpc import RpcRouter, Msg


class RpcApiClass(object):

    def log_something(self, msg, user):
        print msg
        return Msg('OK')

router = RpcRouter({
    'RpcApi': RpcApiClass()
})
