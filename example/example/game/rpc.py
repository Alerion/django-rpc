from djangorpc import RpcRouter, Error, Msg
from djangorpc.exceptions import RpcExceptionEvent


class GameApiClass(object):

    def move(self, x, y, battle_id, user):
        print 'Move in battle #%s' % battle_id
        return {}

    def _extra_kwargs(self, request, *args, **kwargs):
        """
        We can to here something like::

            try:
                battle = Battle.objects.get(pk=kwargs['battle_id'])
            except Battle.DoesNotExist:
                raise RpcExceptionEvent('Invalid battle id!')
        """
        return {
            'battle_id': kwargs['battle_id']
        }


router = RpcRouter(
    {
        'GameApi': GameApiClass(),
    },
    url_namespace='game:rpc')
