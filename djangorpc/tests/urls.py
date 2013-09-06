from django.conf.urls import patterns, include, url
from .rpc import router


urlpatterns = patterns(
    '',
    url(r'^rpc/', include(router.urls, 'rpc')),
)
