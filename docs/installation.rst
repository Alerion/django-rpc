
.. _installation:

Installation
============

You can load application from https://github.com/Alerion/Django-RPC.

1. Add ``rpc`` application to ``INSTALLED_APPS``. Now all required JS files are accessible with Django
``staticfiles`` application.

2. In your base templates add required JS scripts::

    <script src="{% static 'rpc/js/jquery-1.7.2.min.js' %}"></script>
    <script src="{% static 'rpc/js/jquery.util.js' %}"></script>
    <script src="{% static 'rpc/js/jquery.rpc.js' %}"></script>
    <script src="{% static 'rpc/js/jquery.form.js' %}"></script>

3. You can handle all errors in one place and show some message to user::

    //Show error message for RPC exceptions
    jQuery.Rpc.on('exception', function(event){
        alert('Error during RPC request!');
    });

4. Do not forget about CSRF for Ajax.