from django.conf.urls import *
from . import views
from .rpc import router


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^battle/(?P<battle_id>\d+)/$', views.battle, name='battle'),
    url(r'^rpc/(?P<battle_id>\d+)/', include(router.urls, 'rpc')),
]
