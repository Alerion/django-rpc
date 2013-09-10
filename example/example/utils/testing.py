from __future__ import unicode_literals

import json

from django.test.client import Client


class TestRpcClient(Client):

    def call(self, url, action, method, data):
        tid = 1
        rpc_data = {
            'action': action,
            'method': method,
            'data': data,
            'tid': tid
        }

        response = self.post(url, json.dumps(rpc_data), content_type="application/json")

        assert response.json[0]['action'] == action
        assert response.json[0]['method'] == method
        assert response.json[0]['tid'] == tid

        return response

    def request(self, **request):
        response = super(TestRpcClient, self).request(**request)

        try:
            response.json = json.loads(response.content)
        except ValueError:
            pass

        return response
