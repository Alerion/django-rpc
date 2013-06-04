.. _tutorial-part-3:

*********************
Part 3: Useful tricks
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

TBD


Method level
------------

TBD


Decorators
==========

TBD


RpcExceptionEvent
=================

TBD


Passing arguments from URL
==========================

TBD


_pre_execute
============

TBD


Turn off butch
==============

TBD
