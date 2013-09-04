from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^tests/', include('djangorpc.tests.urls', 'tests')),
)
