from decorators import render_to
from main.forms import FeedbackForm

@render_to('main/index.html')
def index(request):
    return {
        'form': FeedbackForm()
    }