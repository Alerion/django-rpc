from django import forms
from rpc.utils.forms import AjaxForm


class FeedbackForm(forms.Form, AjaxForm):
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea())

    def send(self):
        print 'Send!'
