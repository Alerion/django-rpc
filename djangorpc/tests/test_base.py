from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client


class MainTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_base(self):
        api_url = reverse('tests:api')
        router_url = reverse('tests:router')

        response = self.client.get(api_url)
        self.assertEqual(response.status_code, 200)
