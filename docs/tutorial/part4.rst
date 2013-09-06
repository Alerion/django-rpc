.. _tutorial-part-4:

*********************
Part 4: Useful tricks
*********************

Here I'll try show some useful trick that can save you time and explain how Django RPC works.

Real examples of code you can find in `example project <https://github.com/Alerion/Django-RPC/tree/master/example/>`_,
`tricks` app.


.. _passing_extra_arguments:

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

    custom_router = CustomRouter(
        {
            'TricksApi': TricksApiClass(),
            'TricksOneApi': TricksOneApiClass()
        },
        url_namespace='tricks:custom_rpc')

Just to have full example, lets show ``urls.py``::

    from django.conf.urls import patterns, include, url
    from .rpc import custom_router


    urlpatterns = patterns('example.tricks.views',
        url(r'^$', 'index', name='index'),
        url(r'^custom_rpc/', include(custom_router.urls, 'custom_rpc')),
    )

and our template::

    <script src="{% url 'tricks:custom_rpc:jsapi' %}"></script>
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

This tricks allow add argument from URL to every RPC request without changing any JS code.

Why may you need this?
----------------------

For instance, we have some browser game. User can create battle, other can join this battle
and everything happens on page with URL '/battle/100500/', where `100500` is ID of some row
in out `battle` table in database.

You do not want pass battle ID for every RPC call, especially if your `GameApi.move`, `GameApi.hit`,
`GameApi.jump`, `GameApi.next_turn` and other are used a lot in your JS.


What to do?
-----------

Django RPC allows you easy pass extra arguments(our `battle_id`) in URL. All these arguments are
passed to method, that allows you :ref:`pass extra arguments <passing_extra_arguments>`.

Example
-------

At first let our URL-patterns accept arguments from URL::

    urlpatterns = patterns('example.game.views',
        url(r'^battle/(?P<battle_id>\d+)/$', 'battle', name='battle'),
        url(r'^rpc/(?P<battle_id>\d+)/', include(router.urls, 'rpc')),
    )

`battle` view is not related to RPC, just want to show how harmoniously it is.

Our `actions.py` can be like this::

    from djangorpc import RpcRouter, Error, Msg
    from djangorpc.exceptions import RpcExceptionEvent


    class GameApiClass(object):

        def move(self, x, y, battle, user):
            battle.move(x, y, user)
            return {}

        def _extra_kwargs(self, request, *args, **kwargs):
            try:
                battle = Battle.objects.get(pk=kwargs['battle_id'])
            except Battle.DoesNotExist:
                raise RpcExceptionEvent('Invalid battle id!')

            return {
                'battle': battle
            }

    router = RpcRouter(
        {
            'GameApi': GameApiClass(),
        },
        url_namespace='game:rpc')

And in our template just use `battle_id` to create URL to our rpc script::

    <script src="{% url 'game:rpc:jsapi' battle_id %}"></script>
    <script>
        GameApi.move(1, 2);
    </script>


_pre_execute
============

If method has `_pre_execute` attribute, it is executed before method call.
It can be use to make some validation. For now it is used for
:func:`~djangorpc.decorators.login_required` decorator. You can use it to create own decorators.


Set cookie in response
======================

The idea was do not touch HTTP on your action class. It should not know how request and response are
passed. But if you started use it instead of just AJAX requests, you may need set up cookies sometime.
You can use :class:`~djangorpc.responses.RpcHttpResponse`.

Some example::

    class TricksThreeApiClass(object):

        def set_cookie(self, user):
            response = RpcHttpResponse({'msg': 'Hello!'})
            response.set_cookie('rpccookie', '123456')
            return response
