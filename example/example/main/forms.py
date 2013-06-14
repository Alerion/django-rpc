from django import forms
from djangorpc.utils.forms import AjaxForm


class FeedbackForm(forms.Form, AjaxForm):
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea())

    def send(self):
        print 'Send!'


class FileForm(forms.Form, AjaxForm):
    message = forms.CharField(widget=forms.Textarea())
    file = forms.FileField()

    def send(self):
        file = self.cleaned_data['file']
        print 'Send: %s, size: %s' % (file, file.size)
