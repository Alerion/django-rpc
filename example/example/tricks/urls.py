from django.conf.urls import *
from . import views
from .rpc import custom_router, custom_router_one


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^custom_rpc/', include(custom_router.urls, 'custom_rpc')),
    url(r'^custom_rpc_one/', include(custom_router_one.urls, 'custom_rpc_one')),
]
