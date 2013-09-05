from django.conf.urls import patterns, include, url
from .rpc import custom_router, custom_router_one


urlpatterns = patterns(
    'example.tricks.views',
    url(r'^$', 'index', name='index'),
    url(r'^custom_rpc/', include(custom_router.urls, 'custom_rpc')),
    url(r'^custom_rpc_one/', include(custom_router_one.urls, 'custom_rpc_one')),
)
