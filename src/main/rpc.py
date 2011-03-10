from utils.rpc import RpcRouter
from main.forms import FeedbackForm
from utils.rpc import Error, Msg, RpcHttpResponse

class MainApiClass(object):
    
    def func1(self, val, d=123, *args, **kwargs):
        return {
            'val': val,
            'd': d,
            'args': args,
            'kwargs': kwargs.keys()
        }
    
    def func2(self, user):
        return Msg(u'func2')
    
    def submit(self, rdata, user):
        form = FeedbackForm(rdata)
        if form.is_valid():
            form.send()
            response = RpcHttpResponse()
            response.cookies['test-cookie'] = 'TEST'
            return response
        else:
            return Error(form.get_errors())
    
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