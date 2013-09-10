from __future__ import unicode_literals

from django.conf import settings

if not settings.configured:
    settings.configure()

JS_API_URL_NAME = getattr(settings, 'DJANGORPC_JS_API_URL_NAME', 'jsapi')
ROUTER_URL_NAME = getattr(settings, 'DJANGORPC_ROUTER_URL_NAME', 'router')
