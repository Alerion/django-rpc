from django.template.response import TemplateResponse
from .forms import FeedbackForm


def index(request):
    return TemplateResponse(request, 'main/index.html')


def hello(request):
    return TemplateResponse(request, 'main/hello.html')


def form(request):
    context = {
        'form': FeedbackForm()
    }
    return TemplateResponse(request, 'main/form.html', context)
