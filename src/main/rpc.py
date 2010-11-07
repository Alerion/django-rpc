from utils.rpc import RpcRouter

class MainApiClass(object):
    
    def func1(self, val, d=123, *args, **kwargs):
        return {'msg': u'func1'}
    
    def func2(self, user):
        return {}

class OtherApiClass(object):

    def _extra_kwargs(self, request, *args, **kwargs):
        #Hack for extra arguments for methods
        #args and kwargs are parameters after url parsing
        return {
            'request': request
        }
    
    def func1(self, user, request):
        return {}
    
router = RpcRouter('main:router', {
    'MainApi': MainApiClass(),
    'OtherApi': OtherApiClass()
})

class SomeApiClass(object):
    
    def func1(self):
        return {}

class CustomRouter(RpcRouter):
    
    def __init__(self):
        self.url = 'main:custom_router'
        self.actions = {
            'SomeApi': SomeApiClass()
        }
        self.enable_buffer = False
    
    def extra_kwargs(self, request, *args, **kwargs):
        print args, kwargs
        return {}
        
custom_router = CustomRouter()