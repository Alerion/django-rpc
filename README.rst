**********
Django RPC
**********

Django RPC for jQuery. Allows execute some server-side class methods with Javascript in your browser.

Also you can submit forms with jQuery Form Plugin.

It also supports call batching. Django RPC batches together calls which are received within a configurable time frame and sends them in a single request.

You can easy move you current views to RPC methods and use Django RPC instead of mess of AJAX requests.

Inspired by Ext.Direct from ExtJs 3.

`Package Documentation <https://django-rpc.readthedocs.org/>`_

`Github repo <https://github.com/Alerion/django-rpc>`_

Installation
============

Install using pip::

    pip install django-rpc

...or clone the project from github::

    https://github.com/Alerion/django-rpc

1. Add ``djangorpc`` application to ``INSTALLED_APPS`` settings::

    INSTALLED_APPS = (
        ...
        'djangorpc',
    )

Now all required JS files are accessible via Django ``staticfiles`` application.

2. Add jQuery to your page. You can use one from application for quick start::

    <script src="{% static 'djangorpc/js/jquery-1.9.1.min.js' %}"></script>

3. In your base templates add required JS scripts::

    <script src="{% static 'djangorpc/js/jquery.util.js' %}"></script>
    <script src="{% static 'djangorpc/js/jquery.rpc.js' %}"></script>
    <script src="{% static 'djangorpc/js/jquery.form.js' %}"></script>

3. You can handle all errors in one place and show some message to user::

    //Show error message for RPC exceptions
    jQuery.Rpc.on('exception', function(event){
        alert('Error during RPC request: '+event.message);
    });

4. Do not forget about CSRF for Ajax requests.

Example
=======

Let's take a look at a quick example how to use Django RPC application.

We'll create a page which calls server-side method using Django RPC and shows us alert with received message.

Create ``rpc.py`` in your project folder with following code::

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

Add following code to page template::

    <script src="{% url 'jsapi' %}"></script>
    <script>
        MainApi.hello('username', function(resp, sb){
            alert(resp.msg);
        });
    </script>

Reload page and you will see an alert with the message "Hello, username!".

If you get an error 403, you may have forgotten about CSRF.

Here is an example of CSRF cookie injection::

    <script>
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?

                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            },
            dataType: 'json',
            error:function(jqXHR, textStatus, errorThrown){
                alert(textStatus +'\n'+ errorThrown)
            }
        });
    </script>

The working project example you can find in our repo.

Contributing
============

Development for this software happend on github, and the main fork is currently at https://github.com/Alerion/Django-RPC

Contributions are welcome in any format, but using github's pull request system is very highly preferred since it makes review and integration much easier.
