
.. _tutorial-part-1:

Part 1: The Basics
==================

Welcome to tutorial. Here we will try to descripe everything you can do with Django RPC application.
We will create some real application and explain how to use Django RPC. 
Result you can find in `our repo <https://github.com/Alerion/Django-RPC>`_.


Starting off
------------

This tutorial assumes you have created some Django project and installed ``rpc`` application;
if not see :ref:`installation instructions <installation>`.

Out project is some simple system to work with tickets, very simple. Create ``main`` application in project 
and add some models to ``main/models.py``::

    from django.db import models


    class Project(models.Model):
        title = models.CharField(max_length=250)

        def __unicode__(self):
            return self.title


    class Ticket(models.Model):
        project = models.ForeignKey(Project)
        title = models.CharField(max_length=250)
        description = models.TextField()
        file = models.FileField(upload_to='uploads/tickets/')
        created = models.DateTimeField(auto_now_add=True)

        def __unicode__(self):
            return self.title


    class Comment(models.Model):
        ticket = models.ForeignKey(Ticket)
        content = models.TextField()
        created = models.DateTimeField(auto_now_add=True)

We do not need them now. It is just to make out project a little bit real.

First API class
---------------

Idea of `RPC <http://en.wikipedia.org/wiki/Remote_procedure_call>`_ to execute some server-side functions
from client in easy way. In our case we will execute classes' methods from browser with Javascript. 
Lets create some simple class in ``main/actions.py``::

    from rpc import RpcRouter, Error, Msg


    class MainApiClass(object):

        def hello(self, username):
            return Msg(u'Hello %s' % username)


    router = RpcRouter('main:router', {
        'MainApi': MainApiClass(),
    })

And our router to ``main/urls.py``::

    from django.conf.urls import patterns, include, url
    from actions import router


    urlpatterns = patterns('example.main.views',
        url(r'^$', 'index', name='index'),
        url(r'^router/$', router, name='router'),
        url(r'^router/api/$', router.api, name='api'),
    )

Now lets find out we have done,

``MainApiClass`` is just Python class, whos methods we are going to call with Javascript.
I hope it is clear what ``hello`` method going to do. As out application was inspired with ExtJs Direct,
we will call our classess ``actions`` too. Action method should return Python dictionary
(with some exceptions, we will discuss this later).

:class:`~rpc.responses.Msg` and :class:`~rpc.responses.Error`
are just distionary subclasses and save response message in ``msg`` and ``error`` keys respectively;
they are used to some kind of standart in our project and you can add any extra values to these dictionaries.

:class:`~rpc.RpcRouter` is class that helps "connect" our server-side and client-side. First argument is URL-pattern name, or something we can pass to Django ``reverse`` function to get URL, which client should use to send requests; you can see this URL-pattern in ``main/urls.py``. ``main:router`` is used because our application URL-pattern is added with ``main`` namespace.
``main:api`` URL-pattern is used to load Javascript objects on page, letter we will see what is going on here.

Second argument is dictionary mapping our action clasess with names we age going to use in Javascript. 
In our example we will something like this::

    MainApi.hello('username')

Using Rpc
---------