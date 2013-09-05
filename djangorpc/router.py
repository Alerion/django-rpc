from __future__ import unicode_literals

import json
from inspect import getargspec

from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from djangorpc.datastructures import RpcMultiValueDict
from djangorpc.exceptions import RpcExceptionEvent
from djangorpc.settings import JS_API_URL_NAME, ROUTER_URL_NAME
from djangorpc.responses import RpcHttpResponse


class RpcRouter(object):
    """
    Router class for RPC.
    """

    def __init__(self, actions={}, url_namespace=None, enable_buffer=True):
        """
        Router class for RPC.

        :param url_namespace: URL pattern namespace where router insance is included.
            Used to get URL which router is connected.
        :param actions: Action classes router should add to RPC API
        :param enable_buffer: Define client should send requests in a batch
        """
        self.url_namespace = url_namespace
        self.actions = actions
        self.enable_buffer = enable_buffer

    def get_urls(self):
        return (
            url(r'^jsapi/$', self.api, name=JS_API_URL_NAME),
            url(r'^router/$', self.dispatch, name=ROUTER_URL_NAME)
        )

    @property
    def urls(self):
        if not hasattr(self, '_urls'):
            self._urls = patterns('', *self.get_urls())
        return self._urls

    def dispatch(self, request, *args, **kwargs):
        if request.POST.get('rpcAction'):
            requests = {
                'action': request.POST.get('rpcAction'),
                'method': request.POST.get('rpcMethod'),
                'data': [dict(request.POST)],
                'tid': request.POST.get('rpcTID'),
                'upload': request.POST.get('rpcUpload') == 'true'
            }

            if requests['upload']:
                requests['files'] = request.FILES
                output = json.dumps(self.call_action(requests, request, *args, **kwargs))
                return HttpResponse('<textarea>%s</textarea>' % output)
        else:
            try:
                requests = json.loads(request.body)
            except (ValueError, KeyError, IndexError):
                # TODO: add loagging and return error event
                requests = []

        if not isinstance(requests, list):
            requests = [requests]

        response = HttpResponse('', mimetype="application/json")

        output = []

        for rd in requests:
            mr = self.call_action(rd, request, *args, **kwargs)

            # FIXME: This looks like a little ugly
            if 'result' in mr and isinstance(mr['result'], RpcHttpResponse):
                for key, val in mr['result'].cookies.items():
                    response.set_cookie(
                        key,
                        val.value,
                        val['max-age'] or None,
                        val['expires'],
                        val['path'],
                        val['domain'],
                        val['secure'])

                mr['result'] = dict(mr['result'])

            output.append(mr)

        response.content = json.dumps(output)

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
        Just set this in template after RPC scripts including:
        <script src="{% url api_url_name %}"></script>
        """
        obj = json.dumps(self, cls=RpcRouterJSONEncoder, url_args=args, url_kwargs=kwargs)
        return HttpResponse(
            'jQuery.Rpc.addProvider(%s)' % obj,
            content_type='application/x-javascript')

    def execute_func(self, func, *args, **kwargs):
        if hasattr(func, '_pre_execute'):
            result = func._pre_execute(func, *args, **kwargs)
            if result is not None:
                return result
        return func(*args, **kwargs)

    def call_action(self, rd, request, *args, **kwargs):
        """
        This method checks parameters of RPC request and call method of action.
        It checks arguments number, method existing, handle RpcExceptionEvent and send
        exception event for RPC.
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
            if isinstance(val, dict) and not isinstance(val, RpcMultiValueDict):
                val = RpcMultiValueDict(val)
            args.append(val)

        if 'files' in rd:
            args.append(rd.get('files'))

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


class RpcRouterJSONEncoder(json.JSONEncoder):
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

    def default(self, obj):
        if isinstance(obj, RpcRouter):
            if obj.url_namespace:
                url_name = '%s:%s' % (obj.url_namespace, ROUTER_URL_NAME)
            else:
                url_name = ROUTER_URL_NAME

            output = {
                'url': reverse(url_name, args=self.url_args, kwargs=self.url_kwargs),
                'enableBuffer': obj.enable_buffer,
                'actions': {}
            }
            for name, action in obj.actions.items():
                output['actions'][name] = self._encode_action(action)
            return output
        else:
            return super(RpcRouterJSONEncoder, self).default(obj)
