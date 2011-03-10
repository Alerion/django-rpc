from django import forms
from utils.forms import AjaxForm

class FeedbackForm(forms.Form, AjaxForm):
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea())
    
    def send(self):
        pass