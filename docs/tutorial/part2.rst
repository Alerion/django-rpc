.. _tutorial-part-2:

Part 2: Handling forms
======================

If you have a lot of AJAX on page, sue you do want submit forms via AJAX too.
Django RPC can help you with this. We use a little bit patched version of
`jQuery Form Plugin <http://malsup.com/jquery/form/>`_.

For now you can't submit forms with file input.


Create form
-----------

Lets crate some feedback form in ``main/forms.py``::

    from django import forms
    from rpc.utils.forms import AjaxForm


    class FeedbackForm(forms.Form, AjaxForm):
        email = forms.EmailField()
        message = forms.CharField(widget=forms.Textarea())

        def send(self):
            print 'Send!'

You can see mixin :class:`~djangorpc.utils.forms.AjaxForm`, it just allows easy get validation errors
in dictionary and return then in response.

We hope you know how to create page and show this form using Django.


Create action method
--------------------

Lets add new method to out ``MainApiClass`` for handling form::

    from djangorpc.decorators import form_handler


    class MainApiClass(object):

        @form_handler
        def submit(self, rdata, user):
            form = FeedbackForm(rdata)
            if form.is_valid():
                form.send()
                return Msg(u'Thank you for feedback.')
            else:
                return Error(form.get_errors())

It is really simple. Remember that :class:`~djangorpc.responses.Error` and :class:`~djangorpc.responses.Msg`
are just a dictionary. If you submit empty form, you will get such response::

    {
        "error": {
            "message": "This field is required.",
            "email": "This field is required."
        }
    }

If form is valid, you will get::

    {
        "msg": "Thank you for feedback."
    }

Decorator :func:`~djangorpc.decorators.form_handler` tells that this method handles form submit. Otherwise you will get
error about incorrect arguments number.


Javascript code
---------------

Now lets make it works. Add following to your page:

.. code-block:: javascript

    jQuery(function($){
        $('#feedback_form').ajaxForm({
            type: 'RPC',
            api: {
                submit: MainApi.submit
            },
            success: function(data, rpc_response, $form){
                console.log(data)
                if (data.success){
                    $form.resetForm();
                } else {
                    for (key in data.error){
                        var $field = $('input[name="'+key+'"], textarea[name="'+key+'"]', $form);
                        var error = '<p class="error_list">'+data.error[key]+'</p>';
                        if ($field.length){
                            $field.before(error);
                        }else{
                            $('.global-errors', $form).prepend(error);
                        }
                    };
                }
            },
            beforeSubmit: function(formData, $Form, options){
                $('p.error_list', $Form).remove();
            }
        });
    });

If you read `jQuery Form Plugin documenation <http://malsup.com/jquery/form/>`_, you know that
``type`` option define the method in which the form data should be submitted(``POST`` or ``GET``).
We've added new method ``RPC`` and new option ``api``, where you can define what RPC method use
to submit form. This is something like it works in ExtJs, so maybe we will add ``load`` method,
to load form initial data.

In ``success`` callback we show validation error or success message.


Form with files
---------------

You can submit forms with files to RPC. It works the same way, just action should accept files
in the second argument. For example::

    class MainApiClass(object):

        @form_handler
        def submit_file(self, rdata, files, user):
            form = FileForm(rdata, files)
            if form.is_valid():
                form.send()
                return Msg(form.cleaned_data['file'].size)
            else:
                return Error(form.get_errors())
