.. _installation:

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

2. Add jQuery to your page. You can use one from our application for a quick start::

    <script src="{% static 'djangorpc/js/jquery-1.9.1.min.js' %}"></script>

3. Add required JS scripts::

    <script src="{% static 'djangorpc/js/utils.js' %}"></script>
    <script src="{% static 'djangorpc/js/rpc.js' %}"></script>
    <script src="{% static 'djangorpc/js/jquery.form.js' %}"></script>

4. You can handle all errors in one place and show some message to user::

    //Show error message for RPC exceptions
    djangoRPC.RPC.observer.addListener('exception', function(event){
        alert('Error during RPC request: '+event.message);
    });

5. Do not forget about CSRF for Ajax requests. Here is an example::

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
