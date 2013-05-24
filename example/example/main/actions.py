from rpc import RpcRouter, Error, Msg
from .forms import FeedbackForm


class MainApiClass(object):

    def hello(self, username, user):
        return Msg(u'Hello, %s' % username)

    def submit(self, rdata, user):
        form = FeedbackForm(rdata)
        if form.is_valid():
            form.send()
            return Msg(u'Thank you for feedback.')
        else:
            return Error(form.get_errors())

    submit._form_handler = True

router = RpcRouter('main:router', {
    'MainApi': MainApiClass(),
})
