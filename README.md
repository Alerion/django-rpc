Django RPC for jQuery. Allows execute some server-side class methods with Javascript in your browser.

Also you can submit forms with jQuery Form Plugin.

It also supports call batching. Django RPC batches together calls which are received within a configurable time frame and sends them in a single request.

You can easy move you current views to RPC methods and use Django RPC instead of mess of AJAX requests.

Inspired by Ext.Direct from ExtJs 3.


Example
=======

Let's take a look at a quick example how to use Django RPC application.

We'll create a page with button, which calls server-side method using Django RPC.

Create `actions.py` in `someapp` application of our `someproject` project with following code:

    from rpc import RpcRouter, Error, Msg


    class MainApiClass(object):

        def hello(self, username, user):
            return Msg(u'Hello, %s!' % username)

Add this to `urls.py`:

    from django.conf.urls import patterns, include, url
    from .actions import router


    urlpatterns = patterns('someproject.someapp.views',
        url(r'^router/$', router, name='router'),
        url(r'^router/api/$', router.api, name='api'),
    )

Add following code to page template:

    <script src="{% url 'main:api' %}"></script>
    <script>
        MainApi.hello('username', function(resp, sb){
            alert(resp.msg);
        });
    </script>

Reload page and you will see alert with message "Hello, username!".
