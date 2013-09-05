from django.conf.urls import patterns, include, url
from .rpc import router


urlpatterns = patterns(
    'example.game.views',
    url(r'^$', 'index', name='index'),
    url(r'^battle/(?P<battle_id>\d+)/$', 'battle', name='battle'),
    url(r'^rpc/', include(router.urls, 'rpc')),
)
