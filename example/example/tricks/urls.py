from django.conf.urls import patterns, include, url
from actions import custom_router


urlpatterns = patterns('example.tricks.views',
    url(r'^$', 'index', name='index'),
    url(r'^custom_router/$', custom_router, name='custom_router'),
    url(r'^custom_router/api/$', custom_router.api, name='custom_router_api'),
)
