from django.utils import simplejson
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from inspect import getargspec

#for jQuery.Rpc
class RpcRouter(object):
    
    def __init__(self, url, actions={}, enable_buffer=True):
        self.url = url
        self.actions = actions
        self.enable_buffer = enable_buffer
        
    def __call__(self, request, *args, **kwargs):
        user = request.user
        POST = request.POST

        if POST.get('extAction'):
            #Forms not supported yet
            requests = {
                'action': POST.get('extAction'),
                'method': POST.get('extMethod'),
                'data': [POST],
                'upload': POST.get('extUpload') == 'true',
                'tid': POST.get('extTID')
            }
    
            if requests['upload']:
                requests['data'].append(request.FILES)
                output = simplejson.dumps(self.call_action(requests, user))
                return HttpResponse('<script>document.domain=document.domain;</script><textarea>%s</textarea>' \
                                    % output)
        else:
            requests = simplejson.loads(request.POST.keys()[0])
            
        if not isinstance(requests, list):
                requests = [requests]
            
        output = [self.call_action(rd, request, *args, **kwargs) for rd in requests]
            
        return HttpResponse(simplejson.dumps(output), mimetype="application/json")    
    
    def action_extra_kwargs(self, action, request, *args, **kwargs):
       if hasattr(action, '_extra_kwargs'):
           return action._extra_kwargs(request, *args, **kwargs)
       return {}
    
    def extra_kwargs(self, request, *args, **kwargs):
        return {
            'user': request.user
        }
        
    def api(self, request, *args, **kwargs):
        obj = simplejson.dumps(self, cls=RpcRouterJSONEncoder, url_args=args, url_kwargs=kwargs)
        return HttpResponse('jQuery.Rpc.addProvider(%s)' % obj)

    def call_action(self, rd, request, *args, **kwargs):
        method = rd['method']
        
        if not rd['action'] in self.actions:
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'result': {'error': 'Undefined action class'}
            }
        
        action = self.actions[rd['action']]
        args = rd.get('data') or []
        func = getattr(action, method)

        extra_kwargs = self.extra_kwargs(request, *args, **kwargs)
        extra_kwargs.update(self.action_extra_kwargs(action, request, *args, **kwargs))
        
        func_args, varargs, varkw, func_defaults = getargspec(func)
        func_args.remove('self')
        for name in extra_kwargs.keys():
            if name in func_args:
                func_args.remove(name)
        
        required_args_count = len(func_args) - len(func_defaults or [])
        if (required_args_count - len(args)) > 0 or (not varargs and len(args) > required_args_count):
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'result': {'error': 'Incorrect arguments number'}
            }
        
        return {
            'tid': rd['tid'],
            'type': 'rpc',
            'action': rd['action'],
            'method': method,
            'result': func(*args, **extra_kwargs)
        }

class RpcRouterJSONEncoder(simplejson.JSONEncoder):
    
    def __init__(self, url_args, url_kwargs, *args, **kwargs):
        self.url_args = url_args
        self.url_kwargs = url_kwargs
        super(RpcRouterJSONEncoder, self).__init__(*args, **kwargs)
    
    def _encode_action(self, o):
        output = []
        for method in dir(o):
            if not method.startswith('_'):
                #f = getattr(o, method)
                data = dict(name=method)
                output.append(data) 
        return output        
    
    def default(self, o):
        if isinstance(o, RpcRouter):
            output = {
                'url': reverse(o.url, args=self.url_args, kwargs=self.url_kwargs),
                'enableBuffer': o.enable_buffer,
                'actions': {}
            }
            for name, action in o.actions.items():
                output['actions'][name] = self._encode_action(action)
            return output
        else:
            return super(RpcActionJSONEncoder, self).default(o)
