from django.conf.urls import *
from . import views
from .rpc import router

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^test_batch/$', views.test_batch, name='test_batch'),
    url(r'^hello/$', views.hello, name='hello'),
    url(r'^js_api/$', views.js_api, name='js_api'),
    url(r'^form/$', views.form, name='form'),
    url(r'^upload_form/$', views.upload_form, name='upload_form'),
    url(r'^rpc/', include(router.urls, 'rpc')),
]
