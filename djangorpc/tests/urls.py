from django.conf.urls import patterns, include, url
from .actions import router


urlpatterns = patterns(
    '',
    url(r'^router/$', router, name='router'),
    url(r'^router/api/$', router.api, name='api'),
)
