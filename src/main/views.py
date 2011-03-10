from decorators import render_to
from main.forms import FeedbackForm

@render_to('main/index.html')
def index(request):
    return {}

@render_to('main/test_main_api.html')
def test_main_api(request):
    return {}

@render_to('main/test_form.html')
def test_form(request):
    return {
        'form': FeedbackForm()
    }
    
@render_to('main/test_batch.html')
def test_batch(request):
    return {}