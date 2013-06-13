.. _tutorial-part-4:

*********************
Part 4: Useful tricks
*********************

Here I'll try show some useful trick that can save you time and explain how Django RPC works.

Real examples of code you can find in `example project <https://github.com/Alerion/Django-RPC/tree/master/example/>`_,
`tricks` app.


Passing extra arguments
=======================

Real situation is when you need access to Django request object in your RPC method.
My idea was do not pass ``request`` to hide how we do method call. So in future we can
use our action class for some other API or send request via WebSocket+Torando
(In current version you can't do this, but with a little patching I did for one project).

I'll show you few ways how to pass extra arguments from request to our methods.


Router level
------------

You can subclass :class:`djangorpc.RpcRouter` and rewrite ``extra_kwargs`` method. Original method looks like this::

    def extra_kwargs(self, request, *args, **kwargs):
        return {
            'user': request.user
        }

You can see ``*args`` and ``**kwargs``. This is important here. These are arguments parsed with
Django URL patterns that are passed to views. So you can get some ID from URL and pass it to every
method. You will see this later.

Lets add ``request`` here::

    from djangorpc import RpcRouter, Error, Msg

    class CustomRouter(RpcRouter):

        def extra_kwargs(self, request, *args, **kwargs):
            print args, kwargs
            return {
                'request': request,
                'user': request.user
            }

    custom_router = CustomRouter()

Now create some actions classes for testing. Do not forget about new ``request`` arguments::

    class TricksApiClass(object):

        def func1(self, user, request):
            return Msg(u'func1')


    class TricksOneApiClass(object):

        def func2(self, val, **kwargs):
            return Msg(u'func2')

And add theme to our router::

    custom_router = CustomRouter('tricks:custom_router', {
        'TricksApi': TricksApiClass(),
        'TricksOneApi': TricksOneApiClass()
    })

Just to have full example, lets show ``urls.py``::

    from django.conf.urls import patterns, include, url
    from actions import custom_router


    urlpatterns = patterns('example.tricks.views',
        url(r'^$', 'index', name='index'),
        url(r'^custom_router/$', custom_router, name='custom_router'),
        url(r'^custom_router/api/$', custom_router.api, name='custom_router_api'),
    )

and our template::

    <script src="{% url 'tricks:custom_router_api' %}"></script>
    <script>
        TricksApi.func1(function(response){
            console.log(response.msg);
        });

        TricksOneApi.func2(1, function(response){
            console.log(response.msg);
        });
    </script>

It works, every method get ``request`` object.


Action level
------------

You can add ``_extra_kwargs`` method for action class. It works like router level::

    class TricksTwoApiClass(object):

        def func3(self, user, request):
            return Msg(u'func3')

        def _extra_kwargs(self, request, *args, **kwargs):
            return {
                'request': request,
                'user': request.user
            }


Method level
------------

You can add ``_extra_kwargs`` attribute for method::

    def extra_kwargs(request, *args, **kwargs):
        return {
            'request': request,
            'user': request.user
        }


    class TricksThreeApiClass(object):

        def func4(self, user, request):
            return Msg(u'func4')

        func4._extra_kwargs = extra_kwargs


Or you can use :func:`~djangorpc.decorators.add_request_to_kwargs` decorator.


RpcExceptionEvent
=================

To raise `exception` event in client, you can use :class:`~djangorpc.exceptions.RpcExceptionEvent`.
For example::

    class TricksThreeApiClass(object):

        def func6(self, user):
            if not user.is_authenticated():
                raise RpcExceptionEvent('Login please!')

and catch it with javascript:

.. code-block:: javascript

    jQuery.Rpc.on('exception', function(event){
        alert('Error during RPC request: '+event.message);
    });

For required login you use decorator :func:`~djangorpc.decorators.login_required`.

Passing arguments from URL
==========================

TBD


_pre_execute
============

TBD
