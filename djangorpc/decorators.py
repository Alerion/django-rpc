from django.utils.translation import ugettext_lazy as _
from .exceptions import RpcExceptionEvent

METHOD_ATTRIBUTES = ['_pre_execute', '_form_handler', '_extra_kwargs']


def copy_method_attributes(from_method, to_method):
    for attr in METHOD_ATTRIBUTES:
        if hasattr(from_method, attr):
            setattr(to_method, attr, getattr(from_method, attr))


def add_request_to_kwargs(method):
    """
    This is decorator for adding request to passed arguments.
    For example::

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
    is authenticated::

        class MainApiClass(object):

            @login_required
            def func2(self, user):
                return Msg(u'func2')
    """
    def check_login(func, *args, **kwargs):
        user = kwargs.get('user')

        if not user or not user.is_authenticated():
            raise RpcExceptionEvent(_(u'Login required'))

    method._pre_execute = check_login
    return method


def form_handler(method):
    """
    This decorator mark method as form handler.
    For example::

        class MainApiClass(object):

            @form_handler
            def submit(self, rdata, user):
                form = FeedbackForm(rdata)
                if form.is_valid():
                    form.send()
                    return Msg(u'Thank you for feedback.')
                else:
                    return Error(form.get_errors())
    """
    method._form_handler = True
    return method
