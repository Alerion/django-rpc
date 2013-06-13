from django.conf.urls import patterns, include, url
from .actions import router


urlpatterns = patterns('example.game.views',
    url(r'^$', 'index', name='index'),
    url(r'^battle/(?P<battle_id>\d+)/$', 'battle', name='battle'),
    url(r'^router/(?P<battle_id>\d+)/$', router, name='router'),
    url(r'^router/api/(?P<battle_id>\d+)/$', router.api, name='api'),
)
