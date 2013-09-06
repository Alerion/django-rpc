.. _tutorial-part-1:

Part 1: The Basics
==================


First API class
---------------

Idea of `RPC <http://en.wikipedia.org/wiki/Remote_procedure_call>`_ to execute some server-side functions
from client in an easy way. In our case we will execute classes' methods from a browser with Javascript.
Lets create some simple class in our ``main`` application. Create ``main/rpc.py`` with the following code::

    from djangorpc import RpcRouter, Error, Msg


    class MainApiClass(object):

        def hello(self, username, user):
            return Msg(u'Hello %s' % username)

``MainApiClass`` is just Python class, whose methods we are going to call with Javascript.
I hope it is clear what the ``hello`` method going to do. As out application was inspired with ExtJs Direct,
we will call our classes ``actions`` too. Action's method should return Python dictionary
(with some exceptions, we will discuss this later).

``request.user`` is passed with arguments from a request. We do not pass ``request`` object, because
we do not want that people use them as Django views. But it is easy tell Django RPC to pass request
if you need or do not pass ``request.user`` if you do not need it.

:class:`~djangorpc.responses.Msg` and :class:`~djangorpc.responses.Error`
are just dictionary subclasses and save a response message in ``msg`` and ``error`` keys respectively;
they are used to make some kind of standard in our project and you can add any extra values to these
dictionaries.

So::

    return Msg(u'Hello %s' % username)

is equal to::

    return {'msg': u'Hello %s' % username}

Now lets connect our action class to URL to handle requests. Add this to ``main/actions.py``::

    router = RpcRouter({
        'MainApi': MainApiClass(),
    },
    url_namespace='main:rpc')

And create ``main/urls.py``::

    from django.conf.urls import patterns, include, url
    from .rpc import router


    urlpatterns = patterns('example.main.views',
        url(r'^$', 'index', name='index'),
        url(r'^rpc/', include(router.urls, 'rpc')),
    )

:class:`~djangorpc.RpcRouter` is class that helps "connect" our server-side and client-side. It generates
some Javascript to use our actions in browser, passes requests to correct action's method and returns
its response to our callback.

Fisrt argument is dictionary mapping our action classes with names we age going to use in Javascript.

Second argument is URL-pattern namespace, that will be used to get URL with Django ``reverse`` function, that client should use to send requests. You can see this URL-pattern in ``main/urls.py``.
``main:rpc`` is used because our application URL-pattern is added with ``main`` namespace, and we included ``router.urls`` with ``rpc`` namespace.
.
In our example we will use something like this::

    MainApi.hello('username')


Using Rpc
---------

Lets create some simple view::

    def hello(request):
        return TemplateResponse(request, 'main/hello.html')

In ``main/hello.html`` we should load generated JS code to call server-side methods::

    <script src="{% url 'main:rpc:jsapi' %}"></script>

We use URL defined before in ``main/urls.py``.

We can call our method::

    MainApi.hello('Username', function(resp, sb){
        alert(resp.msg);
    });

You should see alert with messages "Hellp, Username".


Default arguments and \*args
----------------------------

Action method can have optional arguments or accept ``*args``. Pay attention that ``user`` is passed as
keyword argument, so you should accept ``**kwargs`` according to Python syntax.

Lets add new method to our ``MainApiClass`` class::

    def func1(self, val, d='default', *args, **kwargs):
        print 'val =', val
        print 'd =', d
        print 'args =', args
        return Msg(u'func1')

It does nothing, just show passed arguments.

Lets execute in bowser following JS code::

    MainApi.func1(1, 2, 3, 4, 5)

In Django dev-server output you can see::

    val = 1
    d = 2
    args = (3, 4, 5)

Now execute::

    MainApi.func1(1)

You will see::

    val = 1
    d = default
    args = ()

If you execute ``MainApi.func1()``, you will get error "Incorrect arguments number".

I think is clear what happens. You can play with different arguments number using
our example project from repo.
