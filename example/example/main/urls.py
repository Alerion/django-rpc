from django.conf.urls import patterns, include, url

from .rpc import router


urlpatterns = patterns(
    'example.main.views',
    url(r'^$', 'index', name='index'),
    url(r'^test_batch/$', 'test_batch', name='test_batch'),
    url(r'^hello/$', 'hello', name='hello'),
    url(r'^js_api/$', 'js_api', name='js_api'),
    url(r'^form/$', 'form', name='form'),
    url(r'^upload_form/$', 'upload_form', name='upload_form'),
    url(r'^rpc/', include(router.urls, 'rpc')),
)
