from Cookie import SimpleCookie
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.datastructures import MultiValueDict
from django.utils.translation import ugettext_lazy as _
from inspect import getargspec


class RpcMultiValueDict(MultiValueDict):
    """
    Just allow pass not list values and get only dict as argument
    """

    def __init__(self, key_to_list_mapping={}):
        for key, value in key_to_list_mapping.items():
            if not isinstance(value, (list, tuple)):
                key_to_list_mapping[key] = [value]

        super(MultiValueDict, self).__init__(key_to_list_mapping)


class RpcExceptionEvent(Exception):
    """
    This exception is sent to server as Ext.Direct.ExceptionEvent.
    So we can handle it in client and show pretty message for user.
    Example:

        class MainApiClass(object):

            def func2(self, user):
                if not user.is_authenticated():
                    raise RpcExceptionEvent(u'Permission denied.')

    And you can catch this with:

        jQuery.Rpc.on('exception', function(event){
            alert('ERROR: '+event.message);
        });
    """
    pass


class RpcResponse(dict):
    pass


class Error(RpcResponse):
    """
    Simple responses. Just for pretty code and some kind of "protocol"
    """
    def __init__(self, text, **kwargs):
        super(Error, self).__init__(error=text, **kwargs)


class Msg(RpcResponse):
    """
    Simple responses. Just for pretty code and some kind of "protocol"
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


#for jQuery.Rpc
class RpcRouter(object):
    """
    Router for jQuery.Rpc calls.
    """
    def __init__(self, url, actions={}, enable_buffer=True):
        self.url = url
        self.actions = actions
        self.enable_buffer = enable_buffer

    def __call__(self, request, *args, **kwargs):
        """
        This method is view that receive requests from Ext.Direct.
        """
        POST = request.POST

        if POST.get('rpcAction'):
            #Forms with upload not supported yet
            requests = {
                'action': POST.get('rpcAction'),
                'method': POST.get('rpcMethod'),
                'data': [dict(POST)],
                'upload': POST.get('rpcUpload') == 'true',
                'tid': POST.get('rpcTID')
            }

            if requests['upload']:
                requests['data'].append(request.FILES)
                output = simplejson.dumps(self.call_action(requests, request, *args, **kwargs))
                return HttpResponse('<textarea>%s</textarea>' \
                                    % output)
        else:
            try:
                requests = simplejson.loads(request.POST.keys()[0])
            except (ValueError, KeyError, IndexError):
                requests = []

        if not isinstance(requests, list):
            requests = [requests]

        response = HttpResponse('', mimetype="application/json")

        output = []

        for rd in requests:
            mr = self.call_action(rd, request, *args, **kwargs)

            #This looks like a little ugly
            if 'result' in mr and isinstance(mr['result'], RpcHttpResponse):
                for key, val in mr['result'].cookies.items():
                    response.set_cookie(key, val.value, val['max-age'], val['expires'], val['path'],
                                        val['domain'], val['secure'])
                mr['result'] = dict(mr['result'])

            output.append(mr)

        response.content = simplejson.dumps(output)

        return response

    def action_extra_kwargs(self, action, request, *args, **kwargs):
        """
        Check maybe this action get some extra arguments from request
        """
        if hasattr(action, '_extra_kwargs'):
            return action._extra_kwargs(request, *args, **kwargs)
        return {}

    def method_extra_kwargs(self, method, request, *args, **kwargs):
        """
        Check maybe this method get some extra arguments from request
        """
        if hasattr(method, '_extra_kwargs'):
            return method._extra_kwargs(request, *args, **kwargs)
        return {}

    def extra_kwargs(self, request, *args, **kwargs):
        """
        For all method in ALL actions we add request.user to arguments.
        You can add something else, request for example.
        For adding extra arguments for one action use action_extra_kwargs.
        """
        return {
            'user': request.user
        }

    def api(self, request, *args, **kwargs):
        """
        This method is view that send js for provider initialization.
        Just set this in template after ExtJs including:
        <script src="{% url api_url_name %}"></script>
        """
        obj = simplejson.dumps(self, cls=RpcRouterJSONEncoder, url_args=args, url_kwargs=kwargs)
        return HttpResponse('jQuery.Rpc.addProvider(%s)' % obj, content_type='application/x-javascript')

    def execute_func(self, func, *args, **kwargs):
        if hasattr(func, '_pre_execute'):
            result = func._pre_execute(func, *args, **kwargs)
            if result is not None:
                return result
        return func(*args, **kwargs)

    def call_action(self, rd, request, *args, **kwargs):
        """
        This method checks parameters of Ext.Direct request and call method of action.
        It checks arguments number, method existing, handle RpcExceptionEvent and send
        exception event for Ext.Direct.
        """
        method = rd['method']

        if not rd['action'] in self.actions:
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': 'Undefined action'
            }

        action = self.actions[rd['action']]

        if not hasattr(action, method):
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': 'Undefined method'
            }

        func = getattr(action, method)

        args = []
        for val in (rd.get('data') or []):
            if isinstance(val, dict) and not isinstance(val, MultiValueDict):
                val = RpcMultiValueDict(val)
            args.append(val)

        extra_kwargs = self.extra_kwargs(request, *args, **kwargs)
        extra_kwargs.update(self.action_extra_kwargs(action, request, *args, **kwargs))
        extra_kwargs.update(self.method_extra_kwargs(func, request, *args, **kwargs))

        func_args, varargs, varkw, func_defaults = getargspec(func)
        func_args.remove('self')  # TODO: or cls for classmethod
        for name in extra_kwargs.keys():
            if name in func_args:
                func_args.remove(name)

        required_args_count = len(func_args) - len(func_defaults or [])
        if (required_args_count - len(args)) > 0 or (not varargs and len(args) > len(func_args)):
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': 'Incorrect arguments number'
            }

        try:
            return {
                'tid': rd['tid'],
                'type': 'rpc',
                'action': rd['action'],
                'method': method,
                'result': self.execute_func(func, *args, **extra_kwargs)
            }
        except RpcExceptionEvent, e:
            return {
                'tid': rd['tid'],
                'type': 'exception',
                'action': rd['action'],
                'method': method,
                'message': unicode(e)
            }


class RpcRouterJSONEncoder(simplejson.JSONEncoder):
    """
    JSON Encoder for RpcRouter
    """

    def __init__(self, url_args, url_kwargs, *args, **kwargs):
        self.url_args = url_args
        self.url_kwargs = url_kwargs
        super(RpcRouterJSONEncoder, self).__init__(*args, **kwargs)

    def _encode_action(self, o):
        output = []

        for method in dir(o):
            if not method.startswith('_'):
                data = dict(name=method)
                f = getattr(o, method)
                if hasattr(f, '_form_handler'):
                    data['formHandler'] = getattr(f, '_form_handler')
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
            return super(RpcRouterJSONEncoder, self).default(o)


METHOD_ATTRIBUTES = ['_pre_execute', '_form_handler', '_extra_kwargs']


def copy_method_attributes(from_method, to_method):
    for attr in METHOD_ATTRIBUTES:
        if hasattr(from_method, attr):
            setattr(to_method, attr, getattr(from_method, attr))


def add_request_to_kwargs(method):
    """
    This is decorator for adding request to passed arguments.
    For example:

    class MainApiClass(object):

        @add_request_to_kwargs
        def func2(self, user, request):
            return Msg(u'func2')
    """
    def extra_kwargs_func(request, *args, **kwargs):
        return dict(request=request)

    method._extra_kwargs = extra_kwargs_func
    return method


def login_required(method):
    """
    This docorator add _pre_execute function for checking if user
    is authenticated
    """
    def check_login(func, *args, **kwargs):
        user = kwargs.get('user')

        if not user or not user.is_authenticated():
            raise RpcExceptionEvent(_(u'Login required'))

    method._pre_execute = check_login
    return method


def form_handler(method):
    """
    This decorator mark method as form handler
    """
    method._form_handler = True
    return method