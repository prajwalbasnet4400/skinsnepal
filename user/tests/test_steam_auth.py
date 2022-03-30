from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()

from user.steam_auth import auth, get_uid, associate_user

class TestSteamAuth(TestCase):
    def setUp(self):
        self.steamid64 = '76561198323043075'
        self.login_url = reverse('user:steam_login')
        self.callback_url_session = reverse('user:steam_callback_session')
        self.callback_url = reverse('user:steam_callback')
    
    def test_auth(self):
        response = auth(self.callback_url)
        self.assertEqual(response.status_code, 302)
    
    def test_associate_user(self):
        user = associate_user(self.steamid64)
        self.assertIsInstance(user,USER_MODEL)