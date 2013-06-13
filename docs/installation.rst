.. _installation:

Installation
============

Install using pip::

    pip install DjangoRpc

...or clone the project from github::

    https://github.com/Alerion/Django-RPC.git

1. Add ``djangorpc`` application to ``INSTALLED_APPS`` settings::

    INSTALLED_APPS = (
        ...
        'djangorpc',
    )

Now all required JS files are accessible via Django ``staticfiles`` application.

2. In your base templates add required JS scripts::

    <script src="{% static 'djangorpc/js/jquery-1.7.2.min.js' %}"></script>
    <script src="{% static 'djangorpc/js/jquery.util.js' %}"></script>
    <script src="{% static 'djangorpc/js/jquery.rpc.js' %}"></script>
    <script src="{% static 'djangorpc/js/jquery.form.js' %}"></script>

3. You can handle all errors in one place and show some message to user::

    //Show error message for RPC exceptions
    jQuery.Rpc.on('exception', function(event){
        alert('Error during RPC request: '+event.message);
    });

4. Do not forget about CSRF for Ajax requests.