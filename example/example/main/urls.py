from django.conf.urls import patterns, include, url


urlpatterns = patterns('example.main.views',
    url(r'^$', 'index', name='index')
)