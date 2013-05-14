from django.template.response import TemplateResponse


def index(request):
    return TemplateResponse(request, 'main/index.html')


def hello(request):
    return TemplateResponse(request, 'main/hello.html')
