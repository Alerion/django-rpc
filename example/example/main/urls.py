from django.conf.urls import patterns, include, url
from actions import router


urlpatterns = patterns('example.main.views',
    url(r'^$', 'index', name='index'),
    url(r'^hello/$', 'hello', name='hello'),
    url(r'^form/$', 'form', name='form'),
    url(r'^router/$', router, name='router'),
    url(r'^router/api/$', router.api, name='api'),
)
