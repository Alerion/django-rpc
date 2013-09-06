.. _example:

Example
=======

Let's take a look at a quick example how to use Django RPC application.

We'll create a page with a button, which calls a server-side method using Django RPC.

Create ``rpc.py`` in your project folder with the following code::

    from djangorpc import RpcRouter, Msg


    class MainApiClass(object):

        def hello(self, username, user):
            return Msg(u'Hello, %s!' % username)

    rpc_router = RpcRouter({
        'MainApi': MainApiClass(),
    })

Add this to ``urls.py``::

    from django.conf.urls import patterns, include, url
    from rpc import rpc_router


    urlpatterns = patterns('someproject.someapp.views',
        url(r'^rpc/', include(rpc_router.urls))
    )

Add the following code to the page template::

    <script src="{% url 'jsapi' %}"></script>
    <script>
        MainApi.hello('username', function(resp, sb){
            alert(resp.msg);
        });
    </script>

Reload the page and you will see an alert with the message "Hello, username!".

The working project example you can find in our repo https://github.com/Alerion/Django-RPC.
