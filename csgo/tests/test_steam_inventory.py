from django.test import TestCase
from csgo.logic.steam_inventory import InventoryItemLogic
from django.contrib.auth import get_user_model
from csgo.models import Item


USER_MODEL = get_user_model()


class TestInventoryItemLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        Item.get_update()
        cls.user = USER_MODEL.objects.create(username='ONION',
                                             avatar='https://avatars.cloudflare.steamstatic.com/264a3bf942e51db3e8d1a960573b4e6dda124c5f_full.jpg',
                                             steamid64='76561198323043075',
                                             phone='0000000000')
        cls.logic = InventoryItemLogic(cls.user)
    
    def test_get_inventory_data(self):
        data = self.logic.get_inventory_data()
        self.assertEqual(data['success'],1)
    
    def test_update_inventory(self):
        self.logic.update_inventory()