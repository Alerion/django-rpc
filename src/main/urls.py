from django.conf.urls.defaults import *
from rpc import router, custom_router

urlpatterns = patterns('main.views',
    url(r'^$', 'index', name='index'),
    url(r'^router/$', router, name='router'),
    url(r'^router/api/$', router.api, name='api'),
    url(r'^custom_router/$', custom_router, name='custom_router'),
    url(r'^custom_router/api/$', custom_router.api, name='custom_router_api'),          
)