from django.test import TestCase, Client
from django.urls import reverse

class TestSteamLoginUrl(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('user:steam_login')


    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,302)